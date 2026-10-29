from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import PlantTask
from .services import generate_daily_tasks, get_user_plant_names, get_all_complete_tasks

@login_required
def schedule_dashboard(request):
    today = timezone.localdate() #In localhost, user is allowed to change/swap local time
    #noted that settings.py timezone is using UTC and not Asia/Jakarta
    
    generate_daily_tasks(request.user, today)
    pending_tasks = PlantTask.objects.filter(user=request.user, due_date=today).order_by('is_completed', 'id')
    care_logs = PlantTask.objects.filter(user=request.user, is_completed=True).order_by('-completed_at')

    context = {
        'pending_tasks': pending_tasks,
        'today': today,
        #Dari hasil return suatu arr tanpa isi sorted akan menghasilkan nilai empty/false
        #Sehingga needs_plant bersifat true dan menampilkan task "Tambahkan 1 tanaman ke Jurnal"
        'needs_plant': not get_user_plant_names(request.user),
        'care_logs': care_logs,
        'all_completed': get_all_complete_tasks(request.user, today), 
    }
    return render(request, 'schedules/dashboard.html', context)

@login_required
def complete_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(PlantTask, id=task_id, user=request.user)
        if not task.is_completed:
            task.mark_as_done()
    return redirect('schedules:index')