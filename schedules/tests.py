import datetime
from django.test import TestCase
from django.contrib.auth import get_user_model
from notes.models import Note
from schedules.models import PlantTask
from schedules.services import generate_daily_tasks

from django.db import IntegrityError
from unittest.mock import patch

class DailyTaskTest(TestCase):
    def setUp(self):
        U = get_user_model()
        self.u = U.objects.create_user(username='a', email='a@a.com', password='x')
        for n in ['Cabai', 'Basil', 'Mawar']:
            Note.objects.create(user=self.u, plant_name=n, title=n)

    def test_four_categories_idempotent(self):
        d = datetime.date(2026, 10, 23)
        generate_daily_tasks(self.u, d); generate_daily_tasks(self.u, d)
        qs = PlantTask.objects.filter(user=self.u, due_date=d)
        self.assertEqual(qs.count(), 4)
        self.assertEqual(set(qs.values_list('task_type', flat=True)), {'SIRAM','PUPUK','POT','PANTAU'})

    def test_new_day_new_tasks(self):
        generate_daily_tasks(self.u, datetime.date(2026,10,23))
        self.assertEqual(PlantTask.objects.filter(due_date= datetime.date(2026,10,23)).order_by('is_completed', 'id').count(), 4)
        generate_daily_tasks(self.u, datetime.date(2026,10,24))
        self.assertEqual(PlantTask.objects.filter(due_date= datetime.date(2026,10,24)).order_by('is_completed', 'id').count(), 4)
        self.assertEqual(PlantTask.objects.count(), 8)

    def test_no_plants_no_tasks(self):
        Note.objects.all().delete()
        self.assertEqual(generate_daily_tasks(self.u), [])

    def test_needs_plant_task(self):
        Note.objects.all().delete()
        self.client.force_login(self.u)
        r = self.client.get('/schedules/')
        self.assertTrue(r.context['needs_plant'])
        self.assertContains(r, 'Tambahkan 1 tanaman ke Jurnal')
        Note.objects.create(user=self.u, plant_name='Cabai', title='c')
        r = self.client.get('/schedules/')
        self.assertFalse(r.context['needs_plant'])
        self.assertNotContains(r, 'Tambahkan 1 tanaman ke Jurnal')
        self.assertEqual(len(r.context['pending_tasks']), 4)

    def test_view(self):
        self.client.force_login(self.u)
        r = self.client.get('/schedules/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context['pending_tasks']), 4)
        t = r.context['pending_tasks'][0]
        self.client.post(f'/schedules/complete-task/{t.id}/')
        r = self.client.get('/schedules/')
        self.assertEqual(len(r.context['pending_tasks']), 4)
        self.assertEqual(len(r.context['care_logs']), 1)
        
    # @patch('schedules.services.PlantTask.objects.create')
    # def test_generate_daily_tasks_integrity_error(self, mock_create):
    #     mock_create.side_effect = IntegrityError #Idk what is this mock_create do, but I think it's used for call an Error
    #     result = generate_daily_tasks(self.u, datetime.date(2026, 10, 28))
        
    #     self.assertEqual(result, [])
        
    def test_plant_task_str_representation(self):
        task = PlantTask.objects.create(
            user=self.u,
            plant_name='Cabai',
            task_type='SIRAM',
            due_date=datetime.date(2026, 10, 28)
        )
        
        self.assertEqual(str(task), f"[{task.get_task_type_display()}] Cabai")
