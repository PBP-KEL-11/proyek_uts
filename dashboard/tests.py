from django.test import TestCase
from django.urls import reverse

from dashboard.models import GreenTrack
from authentication.models import User
# Create your tests here.

class DashboardTest(TestCase):
    
    def setUp(self):
        self.testUser = User.objects.create(
            username = "test-user",
            password = "88TestPassword88",
            email = "testuser@gmail.com"
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
        
    def test_admin_greentrack_dashboard_page(self):
        response = self.client.get(reverse("dashboard:show_admin_greentrack_cards"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/admin_greentrack_dashboard.html")
        
    def test_admin_user_dashboard_page(self):
        response = self.client.get(reverse("dashboard:show_admin_users_cards"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/admin_user_dashboard.html")
        
    def test_create_greentrack_page(self):
        response = self.client.get(reverse("dashboard:create_greentrack"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/create_greentrack.html")
        
    def test_index_page(self):
        response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/index.html")
