from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import PlantTask

@login_required
def schedule_dashboard(request):
    # Mengambil task yang belum selesai untuk Daily Task
    pending_tasks = PlantTask.objects.filter(user=request.user, is_completed=False).order_by('due_date')
    
    # Mengambil task yang sudah selesai untuk Plant Care Log
    care_logs = PlantTask.objects.filter(user=request.user, is_completed=True).order_by('-completed_at')

    context = {
        'pending_tasks': pending_tasks,
        'care_logs': care_logs,
    }
    return render(request, 'schedules/dashboard.html', context)

@login_required
def complete_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(PlantTask, id=task_id, user=request.user)
        task.mark_as_done()
    return redirect('schedules:index')