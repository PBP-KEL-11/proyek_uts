from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from dashboard.models import GreenTrack
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib import messages

from plants.models import GardenPlant
from notes.models import Note
from dashboard.forms import GreenTrackForm
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
                "username":str(greentrack.user),
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
    return render(request, "dashboard/admin_greentrack_detail.html", context)

def index(request):
    return render(request, "dashboard/index.html")
    
def get_user_greentracker_json(request):
    greentracker = GreenTrack.filter(user=request.user)
    
    greentrack_data = []
    for greentrack in greentracker:
        greentrack_data.append({
            "pk":str(greentrack.user.id),
            "fields": {
                "username":str(greentrack.user),
                "current_xp":greentrack.current_xp,
                "xp_max":greentrack.xp_max,
                "active_badge":greentrack.active_badge,
                "current_level":greentrack.current_level,
                "level_number": greentrack.level_number,
                "streak":greentrack.streak
            }
        })
    return JsonResponse(greentrack_data, safe=False)

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
                "user":str(garden_plant.user),
                "plant":str(garden_plant.plant),
                "notes":garden_plant.notes,
                "last_watered":garden_plant.last_watered,
                "added_at":garden_plant.added_at,
            }
        })
    return JsonResponse(garden_plants_data, safe=False)

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

@require_POST
def create_greentrack_AJAX(request):
    form = GreenTrackForm(request.POST)
    if form.is_valid():
        greentrack=form.save()
        return JsonResponse({
            "message":"Kamu Berhasil Mendaftarkan Diri ke Green Track!", "pk":str(greentrack.id)
        }, status=201)
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

def create_greentrack(request):
    form = GreenTrackForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("dashboard:index")
    context = {"form":form}
    return render(request, "dashboard/create_greentrack.html", context)

def update_greentrack(request, id):
    greentrack = get_object_or_404(GreenTrack, pk=id)
    form = GreenTrackForm(request.POST or None, instance=greentrack)
    if form.is_valid():
        form.save()
        return redirect("dasboard:index")
    context = {"form":form}
    return render(request, "update_greentrack.html", context)   

def delete_greentrack(request, id):
    greentrack = get_object_or_404(GreenTrack, pk=id) 
    if request.method == "POST":
        greentrack.delete()
        messages.success(request, "Green Track Berhasil Dihapus!")
        return redirect("main:index")
    return redirect("main:index")

