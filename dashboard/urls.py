from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('admin-dashboard/', views.show_admin_greentrack_cards, name='show_admin_greentrack_cards'),
    path('admin-dashboard-details/', views.show_admin_greentrack_details, name="show_admin_greentrack_details"),
    path('greentrack/', views.show_user_greentrack_details, name="show_user_greentrack_details"),
    path('test/', views.show_green_track_test, name="show_green_track_test"),
]