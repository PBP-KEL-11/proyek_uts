from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from dashboard.models import GreenTrack
from authentication.models import User
# Create your views here.


def show_green_track_test(request):
    context = {"title":"Green Track Test"}
    return render(request, "test.html", context)

def show_admin_greentrack_cards(request):
    query = request.GET.get("title", "").strip()
    context = {
        "title":"Admin Dashboard",
        "query":query
    }
    return render(request, "admin_dashboard.html", context)


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
                "username":greentrack.user.username,
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
        "greentrack":greentrack
    }
    return render(request, "admin_green_track_detail.html", context)

def show_user_greentrack_details(request, id):
    greentrack = get_object_or_404(GreenTrack, pk=id)
    context = {
        "greentrack":greentrack
    }
    return render(request, "green_track.html", context)

def show_greentrack_component(request):
    return render(request, "green_track_card.html")
