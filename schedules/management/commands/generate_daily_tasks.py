from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from schedules.services import generate_daily_tasks


class Command(BaseCommand):
    help = 'Membuat daily tasks (4 kategori) hari ini untuk semua user. Opsional, bisa dijadwalkan lewat cron.'

    def handle(self, *args, **options):
        total = 0
        for user in get_user_model().objects.filter(is_active=True):
            total += len(generate_daily_tasks(user))
        self.stdout.write(self.style.SUCCESS(f'{total} task dibuat.'))
