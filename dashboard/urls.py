from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('admin-dashboard/', views.show_admin_greentrack_cards, name='show_admin_greentrack_cards'),
    path('admin-dashboard-details/<str:id>', views.show_admin_greentrack_details, name="show_admin_greentrack_details"),
    path('api/greentracks/', views.get_greentrack_json, name="get_greentrack_json"),
    path('greentrack/<str:id>', views.show_user_greentrack_details, name="show_user_greentrack_details"),
    path("", views.index, name="index"),
    path("tanaman/<int:plant_id>/",views.plant_detail,name="plant_detail",),
    path("tanaman/<int:plant_id>/siram/",views.mark_watered,name="mark_watered",),
]