import random

from django.db import IntegrityError, transaction
from django.utils import timezone
from django.db.models import Count, F, Min, Q
from notes.models import Note
from .models import PlantTask


def get_user_plant_names(user):
    """
    Sumber daftar tanaman milik user.
    Saat ini diambil dari catatan (Note) yang statusnya belum 'done'.
    Kalau nanti modul Plants sudah punya model sendiri, cukup ganti isi fungsi ini.
    """
    names = (
        Note.objects.filter(user=user)
        .exclude(status=Note.Status.DONE)
        .values_list('plant_name', flat=True)
        .distinct()
    )
    return sorted(set(names))

def all_completed_message():
    message = [
        "All daily tasks have been completed!! See you tomorrow :D",
        "You have completed all tasks. Keep it up!",
        "Easy going, right? Add 1 more plant won't be that bad...",
        "Your plants feel happy :D",
    ]
    return message[int(random.random()*len(message))]
    
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
    completed = (
        PlantTask.objects.filter(user=user, is_completed=True, due_date=today).count()
    )
    return (completed == 4)

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

def generate_daily_tasks(user, date=None):
    """
    Pastikan user punya tepat 1 task untuk SETIAP kategori (SIRAM, PUPUK, POT, PANTAU)
    pada tanggal `date` (default: hari ini). Maksimal 4 task per hari.

    Aman dipanggil berkali-kali (idempotent): kategori yang sudah ada tidak dibuat ulang.
    """
    #Setelah ditinjau, membuat 4 task per hari dengan tanaman tertentu saja itu tidak mengikuti dengan prosedur
    #Atau alasan utama dibuatnya website Tanamin ini. Dengan demikian, seluruh task pada setiap tanaman akan tetap
    #ditampulkan. Namun hal tersebut akan membuat daily task ini menjadi sangat panjang jika seandainya jumlah tanaman
    #terlalu banyak yang akan mengeluarkan sebanyak n*4 task.
    
    #To do list:
    #
    date = date or timezone.localdate()
    plants = get_user_plant_names(user)
    if not plants:
        return []

    created = []
    for task_type, _label in PlantTask.TASK_CHOICES:
        if PlantTask.objects.filter(user=user, task_type=task_type, due_date=date).exists():
            continue

        # Seed deterministik: pada hari yang sama pilihan tanaman selalu sama,
        # tapi berganti di hari berikutnya.
        rng = random.Random(f'{user.pk}-{date.isoformat()}-{task_type}')
        try:
            with transaction.atomic():
                created.append(
                    PlantTask.objects.create(
                        user=user,
                        plant_name=rng.choice(plants),
                        task_type=task_type,
                        due_date=date,
                    )
                )
        except IntegrityError:
            # Request lain sudah membuatnya lebih dulu (race condition) -> abaikan.
            pass
    return created
