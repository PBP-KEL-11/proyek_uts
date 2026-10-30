import random
from django.utils import timezone
from django.db.models import Count, F, Min, Q
from notes.models import Note
from .models import PlantTask


def get_user_plant_names(user):
    names = (
        Note.objects.filter(garden_plant__user=user)
        .exclude(status=Note.Status.DONE)
        .values_list('plant_name', flat=True)
        .distinct()
    )
    return sorted(set(names))

def all_completed_message():
    messageA = [
        "All daily tasks have been completed!!",
        "You have completed all tasks."
    ]
    messageB = [
        "See you tomorrow :D",
        "Keep it up!",
        "Easy right? Add 1 more plant won't be that bad...",
        "Your plants feel happy :D",
    ]
    return messageA[int(random.random()*len(messageA))] + " " + messageB[int(random.random()*len(messageB))]
    
def all_reminder_message(user, today):
    not_completed = PlantTask.objects.filter(user=user, due_date = today, is_completed=False).count()
    message = [
        f"It's already late. You still have {not_completed} available task" + ("" if (not_completed==1) else "s") + " away! Finish them up!",
        ##f"Are you bored on caring your own plant" + "?" if (plants==1) else "s?" + f"\nYou still have {not_completed} tasks right now.",        
    ]
    return message[int(random.random()*len(message))]
 
def unfinished_message(missed_days):
    """Pesan untuk hari-hari yang terlewat. Mengembalikan None jika tidak ada."""
    if missed_days <= 0:
        return None
    if missed_days == 1:
        intro = ("You missed your daily tasks yesterday. Don't worry, your plants "
                 "will still be healthy if you finish all daily tasks today.")
    elif missed_days == 2:
        intro = "You missed your daily tasks twice in a row."
    else:
        intro = "Your plants have been waiting for you for a while."
    plural = "" if missed_days == 1 else "s"
    return f"{intro} (Missed {missed_days} day{plural} in a row)"
 
# Reminder jam 6 sore (waktu lokal sesuai settings.TIME_ZONE)
REMINDER_HOUR = 18
def seconds_until_reminder():
    """Sisa detik sampai 18:00 hari ini; 0 jika sudah lewat."""
    now = timezone.localtime()
    target = now.replace(hour=REMINDER_HOUR, minute=0, second=0, microsecond=0)
    return max(0, int((target - now).total_seconds()))

def get_all_complete_tasks(user, today):
    num_of_tasks = PlantTask.objects.filter(user=user, due_date=today).count()
    completed = (
        PlantTask.objects.filter(user=user, is_completed=True, due_date=today).count()
    )
    
    #0 tasks are not counted as completed mission, it will be marked as add some plants.
    return num_of_tasks > 0 and completed == num_of_tasks

def get_missed_days(user, today):
    """
    Jumlah hari berturut-turut (sebelum hari ini) tanpa semua task selesai.
    Dihitung dari hari terakhir yang tasknya selesai semua. Hari tanpa baris task
    (user tidak membuka dashboard) tetap terhitung terlewat.
    """
    past = PlantTask.objects.filter(user=user, due_date__lt=today)
 
    last_perfect = (
        past.values('due_date')
        .annotate(total=Count('id'), done=Count('id', filter=Q(is_completed=True)))
        .filter(total=F('done'))
        .order_by('-due_date')
        .first()
    )
    if last_perfect:
        return (today - last_perfect['due_date']).days - 1
 
    first_day = past.aggregate(first=Min('due_date'))['first']
    return (today - first_day).days if first_day else 0


#We only want users have 3 different plants as their daily tasks every day
#In case, let the users don't get infinite points for dashboard achievments
DAILY_MISSIONS = 3
def generate_daily_tasks(user, date=None):
    """
    Pilih maksimal DAILY_MISSIONS tanaman berbeda untuk hari `date`, lalu pastikan
    setiap tanaman punya 4 task (SIRAM, PUPUK, POT, PANTAU). Maksimal 3 x 4 = 12 task/hari.
    Jika tanaman user kurang dari 3, semua tanamannya dipakai.
 
    Aman dipanggil berkali-kali: tanaman yang sudah terpilih hari ini
    dipertahankan, dan hanya slot yang kosong yang diisi (mis. user menambah tanaman
    di tengah hari).
    """
    date = date or timezone.localdate()
    plants = get_user_plant_names(user)
    if not plants:
        return []
 
    chosen = set(
        PlantTask.objects.filter(user=user, due_date=date).values_list('plant_name', flat=True)
    )
    slots = DAILY_MISSIONS - len(chosen)
    if slots > 0:
        candidates = [p for p in plants if p not in chosen]
        # Seed deterministik: pada hari yang sama pilihan selalu sama, berganti di hari berikutnya.
        rng = random.Random(f'{user.pk}-{date.isoformat()}')
        chosen.update(rng.sample(candidates, min(slots, len(candidates))))
 
    created = []
    for plant in sorted(chosen):
        for task_type, _label in PlantTask.TASK_CHOICES:
            # get_or_create sudah menangani race condition lewat UniqueConstraint
            task, was_created = PlantTask.objects.get_or_create(
                user=user, plant_name=plant, task_type=task_type, due_date=date,
            )
            if was_created:
                created.append(task)
    return created
 
 
def get_missions(user, date):
    """Kelompokkan task hari ini per tanaman menjadi 'misi' (kartu di dashboard)."""
    order = {code: i for i, (code, _label) in enumerate(PlantTask.TASK_CHOICES)}
    grouped = {}
    for task in PlantTask.objects.filter(user=user, due_date=date):
        grouped.setdefault(task.plant_name, []).append(task)
 
    missions = []
    for plant, tasks in grouped.items():
        tasks.sort(key=lambda t: order.get(t.task_type, 99))
        done = sum(1 for t in tasks if t.is_completed)
        total = len(tasks)
        missions.append({
            'plant_name': plant,
            'tasks': tasks,
            'done': done,
            'total': total,
            'percent': int(done * 100 / total),
            'is_complete': done == total,
        })
    # Misi yang belum selesai di atas, lalu urut nama
    missions.sort(key=lambda m: (m['is_complete'], m['plant_name'].lower()))
    return missions