from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from .views import show_main

# Create your tests here.

class MainTest(TestCase):

    def setUp(self):
        self.response = self.client.get(reverse('main:show_main'))
        self.html = self.response.content.decode()

    def test_page_is_accessible(self):
        self.assertEqual(self.response.status_code, 200)

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")
        self.assertEqual(response.status_code, 404)

    def teset_using_the_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'main/index.html')
        self.assertTemplateUsed(response, 'main/base.html')
        self.assertTemplateUsed(response, 'main/includes/header.html')
        self.assertTemplateUsed(response, 'main/includes/footer.html')
        self.assertTemplateUsed(response, 'main/includes/toast.html')

    def test_page_title(self):
        self.assertContains(self.response, '<title>Tanamin | Rawat Tanamanmu</title>')

    def test_token_csrf_tersedia_untuk_skrip_logout(self):
        self.assertContains(self.response, 'name="csrf-token"')

    def test_framework_and_css_loaded(self):
        self.assertContains(self.response, 'bootstrap@5.3.3')
        self.assertContains(self.response, 'css/main/style.css')

    # header untuk pengunjung

    def test_header_shows_login_and_register(self):
        self.assertContains(self.response, reverse('authentication:login_user'))
        self.assertContains(self.response, reverse('authentication:register'))
        self.assertContains(self.response, 'Login')
        self.assertContains(self.response, 'Register')

    # hero

    def test_hero_shows_title_and_tag(self):
        self.assertContains(self.response, 'Rawat Tanamanmu')
        self.assertContains(self.response, 'Tanpa Terlupa Waktu')
        self.assertContains(self.response, 'Tanam • Tumbuh • Tuai')

    def test_hero_button_for_unauthenticated_user(self):
        self.assertContains(
            self.response,
            f'href="{reverse("authentication:register")}" class="btn-primary">Mulai Sekarang</a>',
        )
        self.assertContains(self.response, 'href="#fitur" class="btn-secondary">Pelajari Fitur</a>')

    def test_pelajari_fitur_button_redirects_to_fitur(self):
        self.assertContains(self.response, 'id="fitur"')
