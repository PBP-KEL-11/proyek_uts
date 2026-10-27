
# dashboard/views.py

from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.utils import timezone

from plants.models import GardenPlant
from notes.models import Note


@login_required
def index(request):
    """Menampilkan kebun milik user dan 3 jurnal terbaru per tanaman."""

    garden_plants = (
        GardenPlant.objects
        .filter(user=request.user)
        .select_related("plant")
        .prefetch_related(
            Prefetch(
                "journal_entries",
                queryset=Note.objects.order_by("-created_at")[:3],
                to_attr="recent_notes",
            )
        )
    )

    return render(
        request,
        "dashboard/index.html",
        {
            "garden_plants": garden_plants,
            "total_plants": garden_plants.count(),
        },
    )


@login_required
def plant_detail(request, plant_id):
    """Menampilkan detail tanaman dan semua jurnalnya."""

    garden_plant = get_object_or_404(
        GardenPlant.objects.select_related("plant"),
        pk=plant_id,
        user=request.user,
    )

    journals = garden_plant.journal_entries.all()

    return render(
        request,
        "dashboard/plant_detail.html",
        {
            "garden_plant": garden_plant,
            "journals": journals,
        },
    )


@login_required
@require_POST
def mark_watered(request, plant_id):
    """Mencatat bahwa tanaman sudah disiram."""

    garden_plant = get_object_or_404(
        GardenPlant,
        pk=plant_id,
        user=request.user,
    )

    garden_plant.last_watered = timezone.now()
    garden_plant.save(update_fields=["last_watered"])

    return JsonResponse({
        "success": True,
        "message": (
            f"{garden_plant.plant.common_name} berhasil disiram!"
        ),
        "last_watered": timezone.localtime(
            garden_plant.last_watered
        ).strftime("%d %b %Y, %H:%M"),
    })
