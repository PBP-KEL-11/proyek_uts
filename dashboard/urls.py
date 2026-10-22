from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('admin-dashboard/', views.show_admin_greentrack_cards, name='show_admin_greentrack_cards'),
    path('admin-dashboard-details/<str:id>', views.show_admin_greentrack_details, name="show_admin_greentrack_details"),
    path('api/greentracks/', views.get_greentrack_json, name="get_greentrack_json"),
    path('greentrack/<str:id>', views.show_user_greentrack_details, name="show_user_greentrack_details"),
    path('test/', views.show_green_track_test, name="show_green_track_test"),
]