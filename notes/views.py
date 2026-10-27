from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import NoteForm
from .models import Note


@login_required
def index(request):
    # Ambil catatan yang terhubung dengan tanaman milik user.
    # Catatan tanpa garden_plant tidak akan muncul di sini.
    notes = Note.objects.filter(garden_plant__user=request.user).select_related(
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

    return render(
        request,
        "notes/index.html",
        {
            "notes": notes,
            "categories": Note.Category.choices,
            "selected_category": category,
            "q": q,
        },
    )


@login_required
def create(request):
    form = NoteForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        note = form.save(commit=False)  # tahan dulu
        note.user = request.user  # isi pemilik
        note.save()
        return redirect("notes:index")
    return render(request, "notes/form.html", {"form": form, "judul": "Tambah Catatan"})


@login_required
def edit(request, pk):
    note = get_object_or_404(
        Note, pk=pk, user=request.user
    )  # catatan orang lain -> 404
    form = NoteForm(request.POST or None, request.FILES or None, instance=note)
    if form.is_valid():
        form.save()
        return redirect("notes:index")
    return render(
        request,
        "notes/form.html",
        {"form": form, "judul": "Edit Catatan", "note": note},
    )


@login_required
def delete(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == "POST":
        if note.image:
            note.image.delete(save=False)  # hapus file fotonya juga
        note.delete()
        return redirect("notes:index")
    return render(request, "notes/confirm_delete.html", {"note": note})
