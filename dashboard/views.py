from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from dashboard.models import GreenTrack
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.views.decorators.http import require_POST
from django.utils import timezone

from plants.models import GardenPlant
from notes.models import Note
# Create your views here.

def show_base(request):
    return render(request, "dashboard/base_dashboard.html")

@login_required
def show_admin_greentrack_cards(request):
    query = request.GET.get("title", "").strip()
    context = {
        "title":"Pemain Greentrack",
        "query":query
    }
    return render(request, "dashboard/admin_greentrack_dashboard.html", context)


def get_greentrack_json(request):
    query = request.GET.get("title", "").strip()
    greentracks = GreenTrack.objects.all()
    
    if query:
        greentracks = greentracks.filter(user__icontains=query)
        
    greentrack_data = []
    for greentrack in greentracks:
        greentrack_data.append({
            "pk":str(greentrack.user.id),
            "fields": {
                "username":greentrack.user,
                "current_xp":greentrack.current_xp,
                "xp_max":greentrack.xp_max,
                "active_badge":greentrack.active_badge,
                "current_level":greentrack.current_level,
                "level_number": greentrack.level_number,
                "streak":greentrack.streak
            }
        })
    return JsonResponse(greentrack_data, safe=False)

def show_admin_greentrack_details(request, id):
    greentrack = get_object_or_404(GreenTrack, pk = id)
    context = {
        "title":"Detail Pengguna",
        "greentrack":greentrack
    }
    return render(request, "dashboard/admin_green_track_detail.html", context)

def show_user_greentrack_details(request, id):
    greentrack = get_object_or_404(GreenTrack, pk=id)
    context = {
        "greentrack":greentrack
    }
    return render(request, "green_track.html", context)


def show_admin_gardenplants_cards(request):
    query = request.GET.get("title", "").strip()
    context = {
        "title":"Tanaman para Pengguna Tanamin",
        "query":query
    }
    return render(request, "dashboard/admin_user_dashboard.html", context)

def get_gardenplants_json(request):
    query = request.GET.get("title", "").strip()
    garden_plants = GardenPlant.objects.all()
    
    if query:
        garden_plants = GardenPlant.filter(user__icontains=query)

    garden_plants_data = []
    for garden_plant in garden_plants:
        garden_plants_data.append({
            "pk":str(garden_plant.user.id),
            "fields":{
                "user":garden_plant.user,
                "plant":garden_plant.plant,
                "notes":garden_plant.notes,
                "last_watered":garden_plant.last_watered,
                "added_at":garden_plant.added_at,
            }
        })

def show_admin_gardenplants_details(request, id):
    username=request.user
    garden_plant = get_object_or_404(
        GardenPlant,
        pk=id,
        user=request.user,
    )
    context = {
        "user":username,
        "garden_plant":garden_plant,
    }
    return render(request, "dashboard/admin_user_detail.html", )

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
