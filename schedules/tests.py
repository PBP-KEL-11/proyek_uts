import datetime
from itertools import count

from django.contrib.auth import get_user_model
from django.test import TestCase

from notes.models import Note
from plants.models import GardenPlant, Plant
from schedules.models import PlantTask
from schedules.services import generate_daily_tasks, get_user_plant_names

_species = count(1)


def make_note(user, name, **extra):
    """Note sekarang terhubung ke user lewat GardenPlant (bukan field user langsung)."""
    plant = Plant.objects.create(species_id=next(_species), common_name=name)
    garden_plant = GardenPlant.objects.create(user=user, plant=plant)
    return Note.objects.create(garden_plant=garden_plant, plant_name=name, title=name, **extra)


class DailyTaskTest(TestCase):
    def setUp(self):
        U = get_user_model()
        self.u = U.objects.create_user(username='a', email='a@a.com', password='x')
        for n in ['Cabai', 'Basil', 'Mawar']:
            make_note(self.u, n)

    def test_three_missions_four_categories_idempotent(self):
        d = datetime.date(2026, 10, 23)
        generate_daily_tasks(self.u, d)
        generate_daily_tasks(self.u, d)
        qs = PlantTask.objects.filter(user=self.u, due_date=d)
        self.assertEqual(qs.count(), 12)
        self.assertEqual(len(set(qs.values_list('plant_name', flat=True))), 3)
        for plant in ['Cabai', 'Basil', 'Mawar']:
            self.assertEqual(
                set(qs.filter(plant_name=plant).values_list('task_type', flat=True)),
                {'SIRAM', 'PUPUK', 'POT', 'PANTAU'},
            )

    def test_max_three_missions_with_many_plants(self):
        for n in ['Melon', 'Labu', 'Apel']:
            make_note(self.u, n)  # total 6 tanaman
        d = datetime.date(2026, 10, 23)
        generate_daily_tasks(self.u, d)
        qs = PlantTask.objects.filter(user=self.u, due_date=d)
        self.assertEqual(qs.count(), 12)
        self.assertEqual(len(set(qs.values_list('plant_name', flat=True))), 3)

    def test_new_day_new_tasks(self):
        generate_daily_tasks(self.u, datetime.date(2026, 10, 23))
        self.assertEqual(PlantTask.objects.filter(due_date=datetime.date(2026, 10, 23)).count(), 12)
        generate_daily_tasks(self.u, datetime.date(2026, 10, 24))
        self.assertEqual(PlantTask.objects.filter(due_date=datetime.date(2026, 10, 24)).count(), 12)
        self.assertEqual(PlantTask.objects.count(), 24)

    def test_no_plants_no_tasks(self):
        Note.objects.all().delete()
        self.assertEqual(generate_daily_tasks(self.u), [])

    def test_plant_names_only_from_own_garden(self):
        other = get_user_model().objects.create_user(username='b', email='b@b.com', password='x')
        make_note(other, 'Kaktus')
        self.assertEqual(get_user_plant_names(self.u), ['Basil', 'Cabai', 'Mawar'])
        self.assertEqual(get_user_plant_names(other), ['Kaktus'])

    def test_done_notes_are_not_used(self):
        make_note(self.u, 'Selesai', status=Note.Status.DONE)
        self.assertNotIn('Selesai', get_user_plant_names(self.u))

    def test_needs_plant_task(self):
        Note.objects.all().delete()
        self.client.force_login(self.u)
        r = self.client.get('/schedules/')
        self.assertTrue(r.context['needs_plant'])
        self.assertContains(r, 'Tambahkan 1 tanaman ke Jurnal')
        make_note(self.u, 'Cabai2')
        r = self.client.get('/schedules/')
        self.assertFalse(r.context['needs_plant'])
        self.assertNotContains(r, 'Tambahkan 1 tanaman ke Jurnal')
        self.assertEqual(len(r.context['missions']), 1)
        self.assertEqual(r.context['missions'][0]['total'], 4)

    def test_view(self):
        self.client.force_login(self.u)
        r = self.client.get('/schedules/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context['missions']), 3)
        t = r.context['missions'][0]['tasks'][0]
        self.client.post(f'/schedules/complete-task/{t.id}/')
        r = self.client.get('/schedules/')
        self.assertEqual(len(r.context['missions']), 3)
        self.assertEqual(len(r.context['care_logs']), 1)
        self.assertEqual(sum(m['done'] for m in r.context['missions']), 1)

    def test_plant_task_str_representation(self):
        task = PlantTask.objects.create(
            user=self.u,
            plant_name='Cabai',
            task_type='SIRAM',
            due_date=datetime.date(2026, 10, 28),
        )
        self.assertEqual(str(task), f"[{task.get_task_type_display()}] Cabai")