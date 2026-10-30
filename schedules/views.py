from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET
from django.utils import timezone
from .models import PlantTask
from .services import (
    generate_daily_tasks, get_user_plant_names, get_all_complete_tasks,
    all_completed_message, all_reminder_message, seconds_until_reminder, get_missed_days,
    unfinished_message
)
from dashboard.views import gain_experience

# Plant Care Log: 10 Logs on first appear, "Expand More" button expands 20 more logs.
LOG_INITIAL = 10
LOG_PAGE = 20

@login_required
@login_required
def schedule_dashboard(request):
    today = timezone.localdate() #In localhost, user is allowed to change/swap local time
    #noted that settings.py timezone is using UTC and not Asia/Jakarta
    
    missed_days = get_missed_days(request.user, today)
    missed_message = None
    if missed_days > 0 and request.session.get('missed_notice_date') != today.isoformat():
        missed_message = unfinished_message(missed_days)
        request.session['missed_notice_date'] = today.isoformat()
 
    generate_daily_tasks(request.user, today)
    pending_tasks = PlantTask.objects.filter(user=request.user, due_date=today).order_by('is_completed', 'id')
    # Ambil 1 baris ekstra untuk tahu apakah masih ada log berikutnya (tanpa COUNT terpisah)
    log_rows = list(_care_log_queryset(request.user)[:LOG_INITIAL + 1])
    care_logs = log_rows[:LOG_INITIAL]
    has_more_logs = len(log_rows) > LOG_INITIAL
 
    all_done = get_all_complete_tasks(request.user, today)
    reminder_wait = seconds_until_reminder()
 
    context = {
        'pending_tasks': pending_tasks,
        'today': today,
        #Dari hasil return suatu arr tanpa isi sorted akan menghasilkan nilai empty/false
        #Sehingga needs_plant bersifat true dan menampilkan task "Tambahkan 1 tanaman ke Jurnal"
        'needs_plant': not get_user_plant_names(request.user),
        'care_logs': care_logs,
        'has_more_logs': has_more_logs,
        'log_initial': LOG_INITIAL,
        'all_completed': all_done,
        'reminder_wait': reminder_wait,
        'show_reminder': reminder_wait == 0 and not all_done,
        'all_completed_message': all_completed_message(),
        'reminder_message': all_reminder_message(request.user, today),
        'missed_message': missed_message,
    }
    return render(request, 'schedules/dashboard.html', context)

@login_required
def complete_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(PlantTask, id=task_id, user=request.user)
        if not task.is_completed:
            task.mark_as_done()
            gain_experience(request)
    return redirect('schedules:index')

def _care_log_queryset(user):
    # '-id' sebagai pembeda agar urutan stabil bila completed_at sama
    return PlantTask.objects.filter(user=user, is_completed=True).order_by('-completed_at', '-id')

@login_required
@require_GET
def more_logs(request):
    """Mengembalikan LOG_PAGE baris log berikutnya (HTML) mulai dari ?offset=N."""
    try:
        offset = max(0, int(request.GET.get('offset', LOG_INITIAL)))
    except ValueError:
        offset = LOG_INITIAL
 
    rows = list(_care_log_queryset(request.user)[offset:offset + LOG_PAGE + 1])
    shown = rows[:LOG_PAGE]
    return JsonResponse({
        'html': render_to_string('schedules/_log_rows.html', {'logs': shown}, request=request),
        'next_offset': offset + len(shown),
        'has_more': len(rows) > LOG_PAGE,
    })