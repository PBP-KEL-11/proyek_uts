import io
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from plants.models import GardenPlant, Plant

from .forms import MAX_IMAGE_MB, NoteForm, shrink_image
from .models import Note

User = get_user_model()
TEMP_MEDIA = tempfile.mkdtemp(prefix="notes_test_media_")


def make_image(name="foto.jpg", fmt="JPEG", size=(40, 30), mode="RGB", content_type=None):
    """Buat file gambar kecil di memori untuk upload."""
    buf = io.BytesIO()
    Image.new(mode, size, (30, 160, 60) if mode == "RGB" else (30, 160, 60, 0)).save(buf, format=fmt)
    ctype = content_type or ("image/png" if fmt == "PNG" else "image/jpeg")
    return SimpleUploadedFile(name, buf.getvalue(), content_type=ctype)


def valid_data(**overrides):
    """Data form lengkap (tanpa foto; foto dikirim lewat argumen files/image)."""
    data = {
        "plant_name": "Cabai Rawit",
        "title": "Daun pertama keluar",
        "category": Note.Category.SAYUR,
        "status": Note.Status.GROWING,
        "planting_method": Note.Method.DIRECT_SOW,
        "planted_date": "2026-10-01",
        "location": "Balkon",
        "content": "Sudah muncul dua daun.",
    }
    data.update(overrides)
    return data


def make_note(user, **overrides):
    fields = dict(
        user=user,
        plant_name="Mawar",
        title="Catatan awal",
        category=Note.Category.BUNGA,
        status=Note.Status.SEEDED,
        planting_method=Note.Method.TRANSPLANT,
        location="Taman",
        content="Isi awal",
    )
    fields.update(overrides)
    return Note.objects.create(**fields)


@override_settings(
    MEDIA_ROOT=TEMP_MEDIA,
    # Hasher MD5 supaya tes tidak lambat (tidak dipakai di produksi).
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
)
class BaseNotesTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(
            "rebecca", email="rebecca@example.com", password="pw12345!"
        )
        self.other = User.objects.create_user(
            "orang_lain", email="lain@example.com", password="pw12345!"
        )
        self.client.login(username="rebecca", password="pw12345!")


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
class NoteModelTest(BaseNotesTest):
    def test_str(self):
        note = make_note(self.user, title="Judul", plant_name="Basil")
        self.assertEqual(str(note), "Judul (Basil)")

    def test_default_ordering_newest_first(self):
        first = make_note(self.user, title="A")
        second = make_note(self.user, title="B")
        self.assertEqual(list(Note.objects.all()), [second, first])

    def test_defaults(self):
        note = Note.objects.create(user=self.user, plant_name="X", title="Y")
        self.assertEqual(note.category, Note.Category.SAYUR)
        self.assertEqual(note.status, Note.Status.PLANNED)
        self.assertEqual(note.planting_method, Note.Method.DIRECT_SOW)


# ---------------------------------------------------------------------------
# Form: semua field wajib diisi (inti perbaikan)
# ---------------------------------------------------------------------------
class NoteFormRequiredTest(BaseNotesTest):
    def test_all_fields_are_required(self):
        """Regresi: __init__ dulu nyasar di dalam Meta sehingga tidak pernah jalan."""
        form = NoteForm()
        for name, field in form.fields.items():
            self.assertTrue(field.required, f"{name} harus wajib")

    def test_valid_with_everything_filled(self):
        form = NoteForm(valid_data(), {"image": make_image()})
        self.assertTrue(form.is_valid(), form.errors)

    def test_each_missing_field_makes_form_invalid(self):
        for field in valid_data():
            with self.subTest(field=field):
                data = valid_data()
                data.pop(field)
                form = NoteForm(data, {"image": make_image()})
                self.assertFalse(form.is_valid())
                self.assertIn(field, form.errors)
                self.assertIn("wajib diisi", form.errors[field][0])

    def test_missing_image_is_invalid(self):
        form = NoteForm(valid_data())
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["image"], ["Foto tanaman wajib diisi."])

    def test_whitespace_only_text_fields_rejected(self):
        for field in ("plant_name", "title", "location", "content"):
            with self.subTest(field=field):
                form = NoteForm(valid_data(**{field: "   "}), {"image": make_image()})
                self.assertFalse(form.is_valid())
                self.assertIn(field, form.errors)

    def test_html_only_text_rejected_after_strip_tags(self):
        """'<b></b>' lolos required Django, tapi kosong setelah strip_tags -> ditolak."""
        messages = {
            "plant_name": "Nama tanaman tidak boleh kosong.",
            "title": "Judul catatan tidak boleh kosong.",
            "location": "Lokasi tanaman wajib diisi.",
            "content": "Isi catatan wajib diisi.",
        }
        for field, msg in messages.items():
            with self.subTest(field=field):
                form = NoteForm(valid_data(**{field: "<b></b>"}), {"image": make_image()})
                self.assertFalse(form.is_valid())
                self.assertEqual(form.errors[field], [msg])

    def test_html_tags_are_stripped(self):
        form = NoteForm(valid_data(title="<script>alert(1)</script>Halo"), {"image": make_image()})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["title"], "alert(1)Halo")

    def test_existing_image_counts_as_filled_on_edit(self):
        note = make_note(self.user, image=make_image().name)
        note.image.save("lama.jpg", make_image(), save=True)
        form = NoteForm(valid_data(), instance=note)  # tidak upload foto baru
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_choice_rejected(self):
        form = NoteForm(valid_data(category="bukan-kategori"), {"image": make_image()})
        self.assertFalse(form.is_valid())
        self.assertIn("category", form.errors)


class NoteFormImageTest(BaseNotesTest):
    def _form(self, image):
        return NoteForm(valid_data(), {"image": image})

    def test_wrong_content_type_rejected(self):
        form = self._form(make_image("a.gif", "GIF", content_type="image/gif"))
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["image"], ["Format harus JPG atau PNG."])

    def test_too_large_rejected(self):
        big = SimpleUploadedFile(
            "besar.jpg", b"0" * (MAX_IMAGE_MB * 1024 * 1024 + 1), content_type="image/jpeg"
        )
        form = self._form(big)
        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)

    def test_fake_image_rejected(self):
        fake = SimpleUploadedFile("palsu.jpg", b"ini bukan gambar", content_type="image/jpeg")
        form = self._form(fake)
        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)

    def test_valid_image_is_converted_to_jpg(self):
        form = self._form(make_image("foto.png", "PNG"))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(form.cleaned_data["image"].name.endswith(".jpg"))


class ShrinkImageTest(TestCase):
    def test_large_image_is_downscaled(self):
        result = shrink_image(make_image(size=(3000, 1500)))
        self.assertEqual(result.content_type, "image/jpeg")
        img = Image.open(result)
        self.assertEqual(max(img.size), 1280)

    def test_small_image_not_enlarged(self):
        img = Image.open(shrink_image(make_image(size=(100, 50))))
        self.assertEqual(img.size, (100, 50))

    def test_transparent_png_gets_white_background(self):
        result = shrink_image(make_image("t.png", "PNG", mode="RGBA"))
        img = Image.open(result)
        self.assertEqual(img.mode, "RGB")
        self.assertEqual(img.getpixel((0, 0)), (255, 255, 255))

    def test_unreadable_file_returned_as_is(self):
        rusak = SimpleUploadedFile("rusak.jpg", b"bukan gambar", content_type="image/jpeg")
        self.assertIs(shrink_image(rusak), rusak)


# ---------------------------------------------------------------------------
# View halaman: index
# ---------------------------------------------------------------------------
class IndexViewTest(BaseNotesTest):
    def test_requires_login(self):
        self.client.logout()
        resp = self.client.get(reverse("notes:index"))
        self.assertEqual(resp.status_code, 302)

    def test_renders_for_logged_in_user(self):
        resp = self.client.get(reverse("notes:index"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "notes/index.html")
        self.assertIn("categories", resp.context)


# ---------------------------------------------------------------------------
# API JSON
# ---------------------------------------------------------------------------
class ApiListTest(BaseNotesTest):
    def test_unauthenticated_gets_403_json(self):
        self.client.logout()
        resp = self.client.get(reverse("notes:api_list"))
        self.assertEqual(resp.status_code, 403)
        self.assertFalse(resp.json()["ok"])

    def test_only_own_notes_returned(self):
        make_note(self.user, title="Milikku")
        make_note(self.other, title="Punya orang")
        data = self.client.get(reverse("notes:api_list")).json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["notes"][0]["title"], "Milikku")

    def test_filter_by_category(self):
        make_note(self.user, title="Bunga", category=Note.Category.BUNGA)
        make_note(self.user, title="Sayur", category=Note.Category.SAYUR)
        data = self.client.get(reverse("notes:api_list"), {"category": "bunga"}).json()
        self.assertEqual([n["title"] for n in data["notes"]], ["Bunga"])

    def test_unknown_category_is_ignored(self):
        make_note(self.user)
        data = self.client.get(reverse("notes:api_list"), {"category": "ngawur"}).json()
        self.assertEqual(data["count"], 1)

    def test_search_title_plant_and_location(self):
        make_note(self.user, title="Panen perdana", plant_name="Tomat", location="Atap")
        make_note(self.user, title="Lain", plant_name="Bayam", location="Dapur")
        url = reverse("notes:api_list")
        for q, expected in (("panen", 1), ("bayam", 1), ("dapur", 1), ("tidak ada", 0)):
            with self.subTest(q=q):
                self.assertEqual(self.client.get(url, {"q": q}).json()["count"], expected)

    def test_serialized_fields(self):
        note = make_note(self.user)
        item = self.client.get(reverse("notes:api_list")).json()["notes"][0]
        self.assertEqual(item["id"], note.pk)
        self.assertEqual(item["category_label"], "Bunga")
        self.assertEqual(item["status_label"], "Seeded")
        self.assertIsNone(item["image_url"])
        self.assertEqual(item["edit_url"], f"/notes/{note.pk}/edit/")
        self.assertEqual(item["delete_url"], f"/notes/{note.pk}/delete/")

    def test_serialized_image_url(self):
        note = make_note(self.user)
        note.image.save("x.jpg", make_image(), save=True)
        item = self.client.get(reverse("notes:api_list")).json()["notes"][0]
        self.assertTrue(item["image_url"].endswith(".jpg"))

    def test_post_not_allowed(self):
        self.assertEqual(self.client.post(reverse("notes:api_list")).status_code, 405)


class ApiCreateTest(BaseNotesTest):
    url = None

    def setUp(self):
        super().setUp()
        self.url = reverse("notes:api_create")

    def test_unauthenticated_gets_403(self):
        self.client.logout()
        resp = self.client.post(self.url, valid_data())
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Note.objects.count(), 0)

    def test_get_not_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_create_success(self):
        resp = self.client.post(self.url, {**valid_data(), "image": make_image()})
        self.assertEqual(resp.status_code, 201)
        body = resp.json()
        self.assertTrue(body["ok"])
        self.assertEqual(body["message"], "Catatan berhasil ditambahkan.")
        note = Note.objects.get()
        self.assertEqual(note.user, self.user)
        self.assertEqual(body["note"]["id"], note.pk)

    def test_one_empty_field_fails_with_400(self):
        for field in valid_data():
            with self.subTest(field=field):
                data = {**valid_data(), "image": make_image()}
                data.pop(field)
                resp = self.client.post(self.url, data)
                self.assertEqual(resp.status_code, 400)
                body = resp.json()
                self.assertFalse(body["ok"])
                self.assertIn(field, body["errors"])
                self.assertTrue(body["message"].startswith("Gagal menambahkan catatan"))
        self.assertEqual(Note.objects.count(), 0)

    def test_missing_image_fails_with_400(self):
        resp = self.client.post(self.url, valid_data())
        self.assertEqual(resp.status_code, 400)
        self.assertIn("image", resp.json()["errors"])
        self.assertEqual(Note.objects.count(), 0)


# ---------------------------------------------------------------------------
# Halaman tambah (create) -- dipakai juga oleh Dashboard
# ---------------------------------------------------------------------------
class CreateViewTest(BaseNotesTest):
    def setUp(self):
        super().setUp()
        self.url = reverse("notes:create")

    def test_requires_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_get_shows_empty_form_without_toast(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["judul"], "Tambah Catatan")
        self.assertNotIn("toast_error", resp.context)

    def test_post_valid_creates_and_redirects(self):
        resp = self.client.post(self.url, {**valid_data(), "image": make_image()})
        self.assertRedirects(resp, reverse("notes:index"))
        note = Note.objects.get()
        self.assertEqual(note.user, self.user)
        self.assertIsNone(note.garden_plant)

    def test_post_with_one_empty_field_shows_failure_toast(self):
        for field in valid_data():
            with self.subTest(field=field):
                data = {**valid_data(), "image": make_image()}
                data.pop(field)
                resp = self.client.post(self.url, data)
                self.assertEqual(resp.status_code, 200)  # tidak redirect = tidak tersimpan
                self.assertTrue(resp.context["toast_error"].startswith("Gagal menambahkan catatan."))
                self.assertContains(resp, 'id="server-toast"')
        self.assertEqual(Note.objects.count(), 0)

    def test_post_without_image_shows_failure_toast(self):
        resp = self.client.post(self.url, valid_data())
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Foto tanaman wajib diisi", resp.context["toast_error"])
        self.assertEqual(Note.objects.count(), 0)

    def _garden_plant(self, user, nickname="Si Hijau"):
        plant = Plant.objects.create(species_id=Plant.objects.count() + 1, common_name="Monstera")
        return GardenPlant.objects.create(user=user, plant=plant, nickname=nickname)

    def test_garden_plant_prefills_name_and_links_note(self):
        gp = self._garden_plant(self.user)
        resp = self.client.get(self.url, {"garden_plant_id": gp.pk})
        self.assertEqual(resp.context["form"].initial["plant_name"], "Si Hijau")

        resp = self.client.post(
            f"{self.url}?garden_plant_id={gp.pk}", {**valid_data(), "image": make_image()}
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Note.objects.get().garden_plant, gp)

    def test_garden_plant_name_falls_back_to_common_name(self):
        gp = self._garden_plant(self.user, nickname="")
        resp = self.client.get(self.url, {"garden_plant_id": gp.pk})
        self.assertEqual(resp.context["form"].initial["plant_name"], "Monstera")

    def test_other_users_garden_plant_is_ignored(self):
        gp = self._garden_plant(self.other)
        resp = self.client.get(self.url, {"garden_plant_id": gp.pk})
        self.assertNotIn("plant_name", resp.context["form"].initial)

    def test_non_numeric_garden_plant_id_is_ignored(self):
        resp = self.client.get(self.url, {"garden_plant_id": "abc"})
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# Halaman edit (inti permintaan: kalau ada field kosong -> tidak boleh tersimpan)
# ---------------------------------------------------------------------------
class EditViewTest(BaseNotesTest):
    def setUp(self):
        super().setUp()
        self.note = make_note(self.user)
        self.note.image.save("lama.jpg", make_image(), save=True)
        self.url = reverse("notes:edit", args=[self.note.pk])

    def test_requires_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_other_users_note_is_404(self):
        self.client.logout()
        self.client.login(username="orang_lain", password="pw12345!")
        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.assertEqual(self.client.post(self.url, valid_data()).status_code, 404)

    def test_get_shows_form_with_note(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["judul"], "Edit Catatan")
        self.assertNotIn("toast_error", resp.context)
        self.assertContains(resp, 'data-has-image="1"')

    def test_edit_success_without_new_photo_keeps_old_photo(self):
        old_name = self.note.image.name
        resp = self.client.post(self.url, valid_data(title="Judul baru"))
        self.assertRedirects(resp, reverse("notes:index"))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Judul baru")
        self.assertEqual(self.note.image.name, old_name)

    def test_edit_with_new_photo_replaces_and_deletes_old_file(self):
        old_name = self.note.image.name
        storage = self.note.image.storage
        self.assertTrue(storage.exists(old_name))
        resp = self.client.post(self.url, {**valid_data(), "image": make_image("baru.jpg")})
        self.assertEqual(resp.status_code, 302)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.image.name, old_name)
        self.assertFalse(storage.exists(old_name))
        self.assertTrue(storage.exists(self.note.image.name))

    def test_edit_with_one_empty_field_is_not_saved_and_shows_toast(self):
        for field in valid_data():
            with self.subTest(field=field):
                data = valid_data(title="JANGAN TERSIMPAN")
                data.pop(field)
                resp = self.client.post(self.url, data)
                self.assertEqual(resp.status_code, 200)  # tetap di halaman edit
                self.assertTrue(resp.context["toast_error"].startswith("Gagal menyimpan catatan."))
                self.assertContains(resp, 'id="server-toast"')
                self.note.refresh_from_db()
                self.assertEqual(self.note.title, "Catatan awal")  # DB tidak berubah

    def test_edit_with_blank_text_is_not_saved(self):
        resp = self.client.post(self.url, valid_data(content="   "))
        self.assertEqual(resp.status_code, 200)
        self.note.refresh_from_db()
        self.assertEqual(self.note.content, "Isi awal")

    def test_toast_message_contains_first_error(self):
        resp = self.client.post(self.url, valid_data(location=""))
        self.assertIn("Lokasi tanaman wajib diisi", resp.context["toast_error"])


# ---------------------------------------------------------------------------
# Hapus
# ---------------------------------------------------------------------------
class DeleteViewTest(BaseNotesTest):
    def setUp(self):
        super().setUp()
        self.note = make_note(self.user)
        self.url = reverse("notes:delete", args=[self.note.pk])

    def test_requires_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_get_shows_confirmation(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "notes/confirm_delete.html")
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())

    def test_post_deletes_note_and_photo_file(self):
        self.note.image.save("hapus.jpg", make_image(), save=True)
        storage, name = self.note.image.storage, self.note.image.name
        resp = self.client.post(self.url)
        self.assertRedirects(resp, reverse("notes:index"))
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())
        self.assertFalse(storage.exists(name))

    def test_post_deletes_note_without_photo(self):
        self.client.post(self.url)
        self.assertEqual(Note.objects.count(), 0)

    def test_cannot_delete_other_users_note(self):
        self.client.logout()
        self.client.login(username="orang_lain", password="pw12345!")
        self.assertEqual(self.client.post(self.url).status_code, 404)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())


class AdminTest(TestCase):
    def test_note_registered_in_admin(self):
        from django.contrib import admin
        self.assertIn(Note, admin.site._registry)