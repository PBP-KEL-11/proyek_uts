from django.test import TestCase
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone
from dashboard.models import GreenTrack
from plants.models import GardenPlant, Plant
from authentication.models import User
# Create your tests here.

class DashboardTest(TestCase):
    
    def setUp(self):
        self.testUser = User.objects.create(
            username = "test-user",
            password = "88TestPassword88",
            email = "testuser@gmail.com"
        )
        
        self.plant = Plant.objects.create(
            species_id = 12345,
            common_name =  "testPlant",
            scientific_name = "testPlantLatin"
        )
        
        self.gardenplant = GardenPlant.objects.create(
            user = self.testUser,
            plant = self.plant,
            nickname = "myPlant",
        )
        
        self.greentrack = GreenTrack.objects.create(
            user = self.testUser,
            greentrack_nickname = "tester",
            greentrack_description = "This description is meant for testing only",
        )
        
    def test_greentrack_model(self):
        self.assertEqual(self.greentrack.user, self.testUser)
        self.assertEqual(self.greentrack.greentrack_nickname, "tester")
        self.assertEqual(self.greentrack.greentrack_description, "This description is meant for testing only")
        self.assertEqual(self.greentrack.active_badge, "Tidak Ada Badge Aktif")
        self.assertEqual(self.greentrack.current_level, "Novice Gardener")
        self.assertEqual(self.greentrack.level_number, 1)
        self.assertEqual(self.greentrack.current_xp, 0)
        self.assertEqual(self.greentrack.xp_max, 250)
        self.greentrack.add_xp()
        self.assertEqual(self.greentrack.current_xp, 100)
        i = 0
        while i<2 :
            self.greentrack.add_xp()
            i+=1
        self.assertEqual(self.greentrack.current_xp, 0)
        self.assertEqual(self.greentrack.current_level, "Adept Gardener")
        self.assertEqual(self.greentrack.level_number, 2)
        
    def test_admin_greentrack_dashboard_page(self):
        response = self.client.get(reverse("dashboard:show_admin_greentrack_cards"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/admin_greentrack_dashboard.html")
        
    def test_admin_user_dashboard_page(self):
        response = self.client.get(reverse("dashboard:show_admin_users_cards"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/admin_user_dashboard.html")
        
    def test_admin_greentrack_detail_page(self):
        response = self.client.get(reverse("dashboard:show_admin_greentrack_details", kwargs={"id":self.testUser.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/admin_greentrack_detail.html")
        self.assertContains(response, self.greentrack.current_level)
        self.assertContains(response, self.greentrack.level_number)
        self.assertContains(response, self.greentrack.current_xp)
        self.assertContains(response, self.greentrack.active_badge)
        self.assertContains(response, self.greentrack.greentrack_description)
        self.assertContains(response, self.greentrack.greentrack_nickname)
        
    def test_user_greentrack_detail_page(self):
        response = self.client.get(reverse("dashboard:show_user_greentrack_details", kwargs={"id":self.testUser.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/greentrack_detail.html")
        self.assertContains(response, self.greentrack.current_level)
        self.assertContains(response, self.greentrack.level_number)
        self.assertContains(response, self.greentrack.current_xp)
        self.assertContains(response, self.greentrack.active_badge)
        self.assertContains(response, self.greentrack.greentrack_description)
        self.assertContains(response, self.greentrack.greentrack_nickname)
