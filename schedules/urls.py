from django.urls import path
from . import views

app_name = 'schedules'

urlpatterns = [
    path('', views.schedule_dashboard, name='index'),
    path('complete-task/<int:task_id>/', views.complete_task, name='complete_task'),
]