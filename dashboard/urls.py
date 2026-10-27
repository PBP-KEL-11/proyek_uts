from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('base_dashboard/', views.show_base, name="base_dashboard"),
    path('admin-greentrack-dashboard/', views.show_admin_greentrack_cards, name='show_admin_greentrack_cards'),
    path('admin-greentrack-details/<str:id>', views.show_admin_greentrack_details, name="show_admin_greentrack_details"),
    path('api/greentracks/', views.get_greentrack_json, name="get_greentrack_json"),
    path('admin-users-dashboard', views.show_admin_gardenplants_cards, name='show_admin_users_cards'),
    path('admin-user-details/<str:id>', views.show_admin_gardenplants_details, name="show_admin_user_details"),
    path('api/users/', views.get_gardenplants_json, name="get_gardenplants_json"),
    path('', views.show_user_greentrack_details, name="show_user_greentrack_details"),
]