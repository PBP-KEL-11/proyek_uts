from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from dashboard.models import GreenTrack
# Create your views here.


def show_green_track_test(request):
    context = {"title":"Green Track Test"}
    return render(request, "test.html", context)

def show_admin_greentrack_cards(request):
    greentracks = GreenTrack.objects.all()
    context = {
        "greentracks":greentracks
    }
    return render(request, "admin_dashboard.html", context)

def show_admin_greentrack_details(request, username):
    greentrack = get_object_or_404(GreenTrack, user=username)
    context = {
        "greentrack":greentrack
    }
    return render(request, "admin_green_track_detail.html", context)

def show_user_greentrack_details(request, username):
    greentrack = get_object_or_404(GreenTrack, user=username)
    context = {
        "greentrack":greentrack
    }
    return render(request, "green_track.html", context)

def show_greentrack_component(request):
    return render(request, "green_track_card.html")
