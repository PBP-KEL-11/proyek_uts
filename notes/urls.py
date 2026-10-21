from django.urls import path
from . import views

app_name = 'notes'
urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.create, name='create'),
    path('<int:pk>/edit/', views.edit, name='edit'),
    path('<int:pk>/delete/', views.delete, name='delete'),
]