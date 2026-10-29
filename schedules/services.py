import random

from django.db import IntegrityError, transaction
from django.utils import timezone

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

def get_all_complete_tasks(user, today):
    completed = (
        PlantTask.objects.filter(user=user, is_completed=True, due_date=today).count()
    )
    return (completed == 4)

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
