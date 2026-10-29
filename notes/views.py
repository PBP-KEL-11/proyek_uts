from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from plants.models import GardenPlant

from .forms import NoteForm
from .models import Note


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _query_notes(request): #mengambil catatan dari database
    """Catatan milik user, dengan filter ?q= ini untuk judul dan ?category= (dipakai halaman & API)."""
    notes = Note.objects.filter(user=request.user).select_related(
        "garden_plant", "garden_plant__plant"
    )
    category = request.GET.get("category", "")
    q = request.GET.get("q", "").strip()

    if category in Note.Category.values:
        notes = notes.filter(category=category)
    if q:
        notes = notes.filter(
            Q(title__icontains=q)
            | Q(plant_name__icontains=q)
            | Q(location__icontains=q)
        )
    return notes, category, q


def _serialize(note):
    """Ubah satu Note jadi dict untuk JsonResponse (dibuat manual, bukan serializer).Mengubah satu objek Note menjadi dictionary biasa"""
    return {
        "id": note.pk,
        "title": note.title,
        "plant_name": note.plant_name,
        "category": note.category,
        "category_label": note.get_category_display(),
        "status": note.status,
        "status_label": note.get_status_display(),
        "planting_method_label": note.get_planting_method_display(),
        "planted_date": note.planted_date.strftime("%d %b %Y"),
        "location": note.location,
        "content": note.content,
        "image_url": note.image.url if note.image else None,
        "edit_url": f"/notes/{note.pk}/edit/",
        "delete_url": f"/notes/{note.pk}/delete/",
    }


def _first_error(form):
    """Pesan error pertama dari form (urut sesuai field), untuk isi toast."""
    for errs in form.errors.get_json_data().values():
        if errs:
            return errs[0]["message"]
    return ""


def _unauthenticated():
    # JANGAN pakai @login_required untuk endpoint JSON: ia mengalihkan (302) ke
    # halaman login berupa HTML sehingga fetch() salah membaca. Balas JSON 403.
    return JsonResponse(
        {"ok": False, "message": "Silakan login terlebih dahulu."}, status=403
    )


# ---------------------------------------------------------------------------
# Halaman (HTML)
# ---------------------------------------------------------------------------
@login_required
def index(request):
    # Halaman hanya merender kerangka. Datanya diambil lewat fetch() ke api_list.
    return render(
        request,
        "notes/index.html",
        {
            "categories": Note.Category.choices,
            "statuses": Note.Status.choices,
            "methods": Note.Method.choices,
            "form": NoteForm(),   # dipakai untuk membangun form di modal
        },
    )


# ---------------------------------------------------------------------------
# Endpoint JSON (AJAX)
# ---------------------------------------------------------------------------
@require_GET
def api_list(request): #mengembalikan daftar catatan dalam bentuk JSON
    if not request.user.is_authenticated:
        return _unauthenticated()

    notes, category, q = _query_notes(request)
    data = [_serialize(n) for n in notes]
    return JsonResponse({"ok": True, "count": len(data), "notes": data})


@require_POST
def api_create(request): # menerima form dri modal
    if not request.user.is_authenticated:
        return _unauthenticated()

    form = NoteForm(request.POST, request.FILES)
    if form.is_valid():
        note = form.save(commit=False)
        note.user = request.user
        note.save()
        return JsonResponse(
            {"ok": True, "message": "Catatan berhasil ditambahkan.", "note": _serialize(note)},
            status=201,
        )

    # 400: kirim error per field supaya bisa ditampilkan di bawah input & di toast
    errors = {
        field: [e["message"] for e in errs]
        for field, errs in form.errors.get_json_data().items()
    }
    return JsonResponse(
        {
            "ok": False,
            "message": "Gagal menambahkan catatan. Periksa kembali isian kamu.",
            "errors": errors,
        },
        status=400,
    )


# ---------------------------------------------------------------------------
# Halaman tambah / edit / hapus (tetap versi biasa, dipakai juga oleh Dashboard)
# ---------------------------------------------------------------------------
@login_required
def create(request):
    # Dashboard mengirim ?garden_plant_id=<id> untuk menautkan catatan ke tanaman di Kebun Saya.
    garden_plant = None
    gp_id = request.GET.get("garden_plant_id")
    if gp_id and gp_id.isdigit():
        garden_plant = GardenPlant.objects.filter(
            pk=gp_id, user=request.user  # hanya tanaman milik sendiri
        ).select_related("plant").first()

    initial = {}
    if garden_plant:
        initial["plant_name"] = garden_plant.nickname or garden_plant.plant.common_name

    form = NoteForm(request.POST or None, request.FILES or None, initial=initial)
    if form.is_valid():
        note = form.save(commit=False)  # tahan dulu
        note.user = request.user  # isi pemilik
        note.garden_plant = garden_plant
        note.save()
        return redirect("notes:index")
    context = {"form": form, "judul": "Tambah Catatan"}
    if request.method == "POST":
        # Form tidak valid -> tampilkan toast gagal (satu field kosong saja sudah cukup).
        context["toast_error"] = f"Gagal menambahkan catatan. {_first_error(form)}".strip()
    return render(request, "notes/form.html", context)


@login_required
def edit(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)  # catatan orang lain -> 404
    old_image = note.image.name if note.image else None
    form = NoteForm(request.POST or None, request.FILES or None, instance=note)
    if form.is_valid():
        note = form.save()
        # Foto diganti / dihapus -> buang file lama agar tidak jadi file yatim
        new_image = note.image.name if note.image else None
        if old_image and old_image != new_image:
            note.image.storage.delete(old_image)
        return redirect("notes:index")
    context = {"form": form, "judul": "Edit Catatan", "note": note}
    if request.method == "POST":
        # Sama seperti tambah: semua field wajib terisi, kalau tidak -> toast gagal.
        context["toast_error"] = f"Gagal menyimpan catatan. {_first_error(form)}".strip()
    return render(request, "notes/form.html", context)


@login_required
def delete(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == "POST":
        if note.image:
            note.image.delete(save=False)  # hapus file fotonya juga
        note.delete()
        return redirect("notes:index")
    return render(request, "notes/confirm_delete.html", {"note": note})

#Buka /notes/        → index()      → kirim kerangka HTML
#   JS jalan         → api_list()   → kirim JSON → JS menggambar kartu
#Klik "Simpan" modal → api_create() → validasi (forms.py) → simpan → JSON 201/400
#Klik ✎ / ✕          → edit() / delete() → halaman biasa → redirect