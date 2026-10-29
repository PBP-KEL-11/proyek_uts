from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('base_dashboard/', views.show_base, name="base_dashboard"),
    path('admin-greentrack-dashboard/', views.show_admin_greentrack_cards, name='show_admin_greentrack_cards'),
    path('admin-greentrack-details/<str:id>', views.show_admin_greentrack_details, name="show_admin_greentrack_details"),
    path('api/greentracks/', views.get_greentrack_json, name="get_greentrack_json"),
    path('admin-users-dashboard/', views.show_admin_gardenplants_cards, name='show_admin_users_cards'),
    path('admin-user-details/', views.show_admin_gardenplants_details, name="show_admin_user_details"),
    path('api/users/', views.get_gardenplants_json, name="get_gardenplants_json"),
    path('greentrack/register', views.create_greentrack, name="create_greentrack"),
    path('api/user-greentrack/', views.get_user_greentracker_json, name="get_user_greentracker_json"),
    path('greentrack/add-ajax', views.create_greentrack_AJAX, name="create_greentrack_AJAX"),
    path('greentrack-details/<uuid:id>', views.show_user_greentrack_details, name="show_user_greentrack_details"),
    path("greentrack/<str:id>/delete/",views.delete_greentrack,name="delete_greentrack"),
    path("greentrack/<str:id>/update/",views.update_greentrack, name="update_greentrack"),
    path("greentrack/gain-xp",views.gain_experience, name="gain_experience"),
    path('', views.index, name="index"),
]