from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .services import get_species_list, PerenualError


import requests

from django.views.decorators.http import require_POST

from .models import Plant, GardenPlant
from .services import get_species_list, get_species_detail, PerenualError

WATERING_OPTIONS = [("frequent", "Sering"), ("average", "Sedang"), ("minimum", "Jarang"), ("none", "Tidak perlu")]
SUNLIGHT_OPTIONS = [("full_shade", "Teduh penuh"), ("part_shade", "Teduh sebagian"),
                    ("sun-part_shade", "Matahari + teduh"), ("full_sun", "Matahari penuh")]


def species_list_page(request):
    filters = {
        "q": request.GET.get("q", "").strip(),
        "watering": request.GET.get("watering", ""),
        "sunlight": request.GET.get("sunlight", ""),
        "indoor": request.GET.get("indoor", ""),
    }
    page = request.GET.get("page", 1)

    try:
        data = get_species_list(page=page, **filters)
        error = None
    except PerenualError as e:
        data, error = {"data": []}, str(e)

    # tandain tanaman yang udah ada di kebun user, biar tombolnya jadi centang
    owned_ids = set()
    if request.user.is_authenticated:
        owned_ids = set(
            GardenPlant.objects.filter(user=request.user).values_list("plant__species_id", flat=True)
        )
    plants = data.get("data", [])
    for p in plants:
        p["in_garden"] = p["id"] in owned_ids

    # querystring tanpa "page" supaya filter nggak hilang pas pindah halaman
    params = request.GET.copy()
    params.pop("page", None)

    return render(request, "species_list.html", {
        "plants": plants,
        "current_page": data.get("current_page", 1),
        "last_page": data.get("last_page", 1),
        "total": data.get("total", 0),
        "filters": filters,
        "qs": params.urlencode(),
        "error": error,
        "watering_options": WATERING_OPTIONS,
        "sunlight_options": SUNLIGHT_OPTIONS,
    })


def _parse_days(d):
    bench = (d.get("watering_general_benchmark") or {}).get("value") or ""
    try:
        return int(str(bench).split("-")[0])
    except ValueError:
        return {"frequent": 3, "average": 7, "minimum": 14, "none": 30}.get(str(d.get("watering")).lower(), 7)


@require_POST
def add_to_garden(request, species_id):
    # cek manual (bukan @login_required) supaya fetch() dapet JSON, bukan redirect HTML
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Login dulu buat nambah tanaman."}, status=401)

    try:
        d = get_species_detail(species_id)
    except requests.RequestException:
        return JsonResponse({"status": "error", "message": "Gagal ambil data tanaman. Coba lagi."}, status=502)

    if not d.get("common_name"):
        return JsonResponse({"status": "error", "message": "Data tanaman ini nggak tersedia di plan API lo."}, status=502)

    img = d.get("default_image") or {}
    plant, _ = Plant.objects.update_or_create(
        species_id=species_id,
        defaults={
            "common_name": d.get("common_name", ""),
            "scientific_name": (d.get("scientific_name") or [""])[0],
            "thumbnail": img.get("thumbnail") or "",
            "watering": d.get("watering") or "",
            "watering_days": _parse_days(d),
            "sunlight": ", ".join(d.get("sunlight") or []),
        },
    )
    _, created = GardenPlant.objects.get_or_create(user=request.user, plant=plant)
    msg = f"{plant.common_name} masuk ke kebun!" if created else f"{plant.common_name} sudah ada di kebun."
    return JsonResponse({"status": "ok", "created": created, "message": msg})