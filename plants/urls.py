from django.urls import path
from . import views

app_name = 'plants'

urlpatterns = [
    path("species/", views.species_list_page, name="species_list"),
    path("add/<int:species_id>", views.add_to_garden, name="add_to_garden")
]