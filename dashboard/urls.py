
# dashboard/urls.py

from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),

    path(
        "tanaman/<int:plant_id>/",
        views.plant_detail,
        name="plant_detail",
    ),

    path(
        "tanaman/<int:plant_id>/siram/",
        views.mark_watered,
        name="mark_watered",
    ),
]
