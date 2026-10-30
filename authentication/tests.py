import uuid
import tempfile
from io import BytesIO
from PIL import Image
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core import mail
from django.urls import reverse
from .forms import EditProfileForm, RegisterForm
from django.db import IntegrityError, transaction
from django.core.files.uploadedfile import SimpleUploadedFile

# Create your tests here.

User = get_user_model()

TEMP_MEDIA = tempfile.mkdtemp()
PASSWORD = "TanaminPBP123#Gasal20262027"
NEW_PASSWORD = "TanaminPBP321#Gasal2627"
AJAX = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}

def create_user(username='tan', email='tan@example.com', password=PASSWORD, **extra):
    extra.setdefault('first_name', 'Tan')
    extra.setdefault('last_name', 'Amin')
    return User.objects.create_user(username=username, email=email, password=password, **extra)

def register(**overrides):
    data = {
        'username': 'hal',
        'email': 'hal@example.com',
        'full_name': 'Hal Tan',
        'password1': PASSWORD,
        'password2': PASSWORD,
    }
    data.update(overrides)
    return data

def edit_data(**overrides):
    data = {
        'username': 'tan',
        'email': 'tan@example.com',
        'first_name': 'Tan',
        'last_name': 'Amin',
    }
    data.update(**overrides)
    return data

def make_image(name='auth_background.png', fmt='PNG'):
    """Membuat file gambar asli (bukan sekadar nama file) untuk uji upload."""
    buffer = BytesIO()
    Image.new('RGB', (10, 10), color='green').save(buffer, format=fmt)
    return SimpleUploadedFile(name, buffer.getvalue(), content_type=f'image/{fmt.lower()}')


# MODEL #

class UserModelTest(TestCase):
    def test_default_role_is_user(self):
        self.assertEqual(create_user().role, 'user')

    def test_primary_key_berupa_uuid(self):
        self.assertIsInstance(create_user().pk, uuid.UUID)

    def test_str_return_username(self):
        self.assertEqual(str(create_user()), 'tan')
   
    def test_photo_is_opsional(self):
        self.assertFalse(create_user().photo)

    def test_email_unique(self):
        create_user()
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user(username='lain', email='tan@example.com', password=PASSWORD)


# FORM #

class RegisterFormTest(TestCase):
    def test_data_valid(self):
        form = RegisterForm(data=register())
        self.assertTrue(form.is_valid(), form.errors)

    def test_full_name_split_into_first_and_last_name(self):
        form = RegisterForm(data=register(full_name='Tan Amin'))
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.first_name, 'Tan')
        self.assertEqual(user.last_name, 'Amin')

    def test_full_name_mononym(self):
        form = RegisterForm(data=register(full_name='Tan'))
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.first_name, 'Tan')
        self.assertEqual(user.last_name, '')

    def test_leading_and_trailing_spaces_in_full_name_are_trimmed(self):
        form = RegisterForm(data=register(full_name='  Tan Amin  '))
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.first_name, 'Tan')
        self.assertEqual(user.last_name, 'Amin')

    def test_full_name_is_required(self):
        form = RegisterForm(data=register(full_name=''))
        self.assertFalse(form.is_valid())
        self.assertIn('full_name', form.errors)

    def test_reject_when_username_is_taken(self):
        create_user(username='hal', email='hal@example.com')
        form = RegisterForm(data=register())
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_reject_when_email_is_taken(self):
        create_user(username='xxx', email='hal@example.com')
        form = RegisterForm(data=register())
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_invalid_email_format_rejected(self):
        form = RegisterForm(data=register(email='bukan-email'))
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_different_pass_confirm_rejected(self):
        form = RegisterForm(data=register(password2='TanaminPBP456'))
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_weak_password_rejected(self):
        for lemah in ('abc', 'password', '1234567890'):
            with self.subTest(password=lemah):
                form = RegisterForm(data=register(password1=lemah, password2=lemah))
                self.assertFalse(form.is_valid())
                self.assertIn('password2', form.errors)

    def test_invalid_char_in_username_rejected(self):
        form = RegisterForm(data=register(username='tan <script>'))
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)


# EDIT PROFILE #

class EditProfileFormTests(TestCase):
    def setUp(self):
        self.user = create_user()

    def test_data_is_valid(self):
        form = EditProfileForm(data=edit_data(first_name='Burhan'), instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_username_and_email_are_required(self):
        form = RegisterForm(data=edit_data(username='', email=''), instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
    
    def test_photo_png_and_jpg_are_accepted(self):
        for nama, fmt in (('a.png', 'PNG'), ('a.jpg', 'JPEG')):
            with self.subTest(format=fmt):
                form = EditProfileForm(
                    data=edit_data(), files={'photo': make_image(nama, fmt)}, instance=self.user
                )
                self.assertTrue(form.is_valid(), form.errors)

    def test_foto_format_gif_ditolak(self):
        form = EditProfileForm(
            data=edit_data(), files={'photo': make_image('a.gif', 'GIF')}, instance=self.user
        )
        self.assertFalse(form.is_valid())
        self.assertIn('photo', form.errors)

    def test_foto_melebihi_batas_ukuran_ditolak(self):
        with patch('authentication.forms.MAX_IMAGE_MB', 0):      # semua file dianggap terlalu besar
            form = EditProfileForm(
                data=edit_data(), files={'photo': make_image()}, instance=self.user
            )
            self.assertFalse(form.is_valid())
            self.assertIn('photo', form.errors)


# VIEW: LOGIN

class LoginViewTests(TestCase):

    def setUp(self):
        self.url = reverse('authentication:login_user')
        self.user = create_user()          # username 'tan'

    def test_get_displays_login_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login.html')

    def test_get_when_already_logged_in_redirects_to_home(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('main:show_main'), fetch_redirect_response=False)

    def test_login_successful(self):
        response = self.client.post(self.url, {'username': 'tan', 'password': PASSWORD}, **AJAX)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['redirect_url'], reverse('main:show_main'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_set_cookie_and_message(self):
        response = self.client.post(self.url, {'username': 'tan', 'password': PASSWORD}, **AJAX)
        self.assertIn('last_login', response.cookies)
        pesan = [str(m) for m in get_messages(response.wsgi_request)]
        self.assertTrue(any('berhasil' in p.lower() for p in pesan))

    def test_wrong_password_returns_400_with_generic_error(self):
        response = self.client.post(self.url, {'username': 'tan', 'password': 'salah'}, **AJAX)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('__all__', data['errors'])
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_unregistered_username_returns_400(self):
        response = self.client.post(self.url, {'username': 'hantu', 'password': PASSWORD}, **AJAX)
        self.assertEqual(response.status_code, 400)
        self.assertIn('__all__', response.json()['errors'])

    def test_error_message_does_not_distinguish_wrong_username_and_password(self):
        salah_password = self.client.post(self.url, {'username': 'tan', 'password': 'x'}, **AJAX).json()
        salah_username = self.client.post(self.url, {'username': 'hal', 'password': 'x'}, **AJAX).json()
        self.assertEqual(salah_password['errors'], salah_username['errors'])

    def test_blank_fields_return_400_bad_request(self):
        response = self.client.post(self.url, {}, **AJAX)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('username', data['errors'])
        self.assertIn('password', data['errors'])


# VIEW: REGISTER

class RegisterViewTests(TestCase):

    def setUp(self):
        self.url = reverse('authentication:register')

    def test_get_displays_registration_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/register.html')

    def test_get_when_already_logged_in_redirects_to_home(self):
        self.client.force_login(create_user())
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('main:show_main'), fetch_redirect_response=False)

    def test_register_successful(self):
        response = self.client.post(self.url, register(), **AJAX)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertTrue(User.objects.filter(username='hal').exists())
        self.assertIn('_auth_user_id', self.client.session)
        self.assertIn('last_login', response.cookies)

    def test_blank_fields_return_400(self):
        response = self.client.post(self.url, {}, **AJAX)
        self.assertEqual(response.status_code, 400)
        for kolom in ('username', 'email', 'full_name', 'password1', 'password2'):
            self.assertIn(kolom, response.json()['errors'])
        self.assertEqual(User.objects.count(), 0)

    def test_duplicate_username_returns_400(self):
        create_user(username='hal', email='lain@example.com')
        response = self.client.post(self.url, register(), **AJAX)
        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.json()['errors'])


# VIEW: PROFILE

class ProfileViewTests(TestCase):

    def setUp(self):
        self.url = reverse('authentication:profile')

    def test_logged_in_user_sees_their_data(self):
        self.client.force_login(create_user())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/profile.html')
        self.assertContains(response, 'tan@example.com')
        self.assertContains(response, 'Amin')

    def test_empty_email_is_displayed_as_dash(self):
        user = create_user()
        User.objects.filter(pk=user.pk).update(email='')
        self.client.force_login(user)
        self.assertContains(self.client.get(self.url), '>-<')

    def test_xss_prevention_in_name_field(self):
        self.client.force_login(create_user(first_name='<script>alert(1)</script>'))
        response = self.client.get(self.url)
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertContains(response, '&lt;script&gt;alert(1)&lt;/script&gt;')

    def test_user_can_only_view_own_data(self):
        create_user(username='lain', email='lain@example.com', first_name='Lain')
        self.client.force_login(create_user())          # login sebagai 'tan'
        response = self.client.get(self.url)
        self.assertContains(response, 'tan@example.com')
        self.assertNotContains(response, 'lain@example.com')


# VIEW: EDIT PROFILE

@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class EditProfileViewTests(TestCase):

    def setUp(self):
        self.url = reverse('authentication:edit_profile')
        self.user = create_user()
        self.client.force_login(self.user)

    def test_anonymous_user_cannot_modify_data(self):
        self.client.logout()
        self.client.post(self.url, edit_data(first_name='hacked'), **AJAX)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Tan')

    def test_get_request_displays_form_with_current_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/edit_profile.html')
        self.assertEqual(response.context['form'].instance, self.user)

    def test_successfully_saves_success_message(self):
        response = self.client.post(self.url, edit_data(first_name='Baru'), **AJAX)
        pesan = [str(m) for m in get_messages(response.wsgi_request)]
        self.assertTrue(any('diperbarui' in p.lower() for p in pesan))

    def test_user_can_only_modify_own_account(self):
        lain = create_user(username='burhan', email='burhan@example.com', first_name='Burhan')
        self.client.post(self.url, edit_data(first_name='Baru'), **AJAX)
        lain.refresh_from_db()
        self.assertEqual(lain.first_name, 'Burhan')


    # ---- foto ----

    def test_upload_photo_valid_saved(self):
        response = self.client.post(self.url, edit_data(photo=make_image()), **AJAX)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.photo.name.startswith('profile_photos/'))

    def test_upload_photo_gif_rejected(self):
        response = self.client.post(self.url, edit_data(photo=make_image('a.gif', 'GIF')), **AJAX)
        self.assertEqual(response.status_code, 400)
        self.assertIn('photo', response.json()['errors'])
        self.user.refresh_from_db()
        self.assertFalse(self.user.photo)

    def test_non_image_file_upload_is_rejected(self):
        palsu = SimpleUploadedFile('virus.png', b'bukan gambar', content_type='image/png')
        response = self.client.post(self.url, edit_data(photo=palsu), **AJAX)
        self.assertEqual(response.status_code, 400)
        self.assertIn('photo', response.json()['errors'])

    def test_oversized_photo_upload_is_rejected(self):
        with patch('authentication.forms.MAX_IMAGE_MB', 0):
            response = self.client.post(self.url, edit_data(photo=make_image()), **AJAX)
        self.assertEqual(response.status_code, 400)
        self.assertIn('photo', response.json()['errors'])

    def test_edit_without_photo_preserves_existing_photo(self):
        self.client.post(self.url, edit_data(photo=make_image()), **AJAX)
        self.user.refresh_from_db()
        nama_foto = self.user.photo.name

        self.client.post(self.url, edit_data(first_name='Baru'), **AJAX)
        self.user.refresh_from_db()
        self.assertEqual(self.user.photo.name, nama_foto)
        self.assertEqual(self.user.first_name, 'Baru')


# VIEW: LOGOUT

class LogoutViewTests(TestCase):

    def setUp(self):
        self.url = reverse('authentication:logout_user')
        self.user = create_user()
        self.client.force_login(self.user)

    def test_last_login_cookie_is_deleted(self):
        self.client.cookies['last_login'] = '2026-10-27 10:00:00'
        response = self.client.post(self.url, **AJAX)
        self.assertEqual(response.cookies['last_login'].value, '')

    def test_protected_page_cannot_be_accessed_after_logout(self):
        self.client.post(self.url, **AJAX)
        response = self.client.get(reverse('authentication:profile'))
        self.assertEqual(response.status_code, 302)


class PasswordResetTest(TestCase):
    def test_forgot_password_page_renders_successfully(self):
        self.assertEqual(self.client.get(reverse('password_reset')).status_code, 200)

    def test_registered_email_triggers_password_reset_email(self):
        create_user()
        response = self.client.post(reverse('password_reset'), {'email': 'tan@example.com'})
        self.assertRedirects(response, reverse('password_reset_done'), fetch_redirect_response=False)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['tan@example.com'])
