import datetime
import io
from pathlib import Path

from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.html import strip_tags
from PIL import Image, ImageOps

from .models import Note

MAX_IMAGE_MB = 2 #foto maksimal 2mb
MAX_SIDE_PX = 1280      # sisi terpanjang setelah diperkecil
JPEG_QUALITY = 80

# Label yang dipakai di pesan error "<label> wajib diisi."
REQUIRED_LABELS = {
    'plant_name': 'Nama tanaman',
    'title': 'Judul catatan',
    'category': 'Kategori',
    'status': 'Status',
    'planting_method': 'Metode tanam',
    'planted_date': 'Tanggal tanam',
    'location': 'Lokasi tanaman',
    'content': 'Isi catatan',
    'image': 'Foto tanaman',
}


def shrink_image(upload):
    """Perkecil foto (sisi terpanjang 1280 px, JPEG kualitas 80).

    Hasilnya jauh lebih kecil dari file asli, jadi folder media/ tidak cepat penuh.
    Kalau Pillow gagal membaca file, kembalikan file aslinya apa adanya.
    """
    try:
        img = Image.open(upload) #pillow membuka file foto
        img = ImageOps.exif_transpose(img)          # hormati orientasi dari kamera HP sehingga dia ga miring
        img.thumbnail((MAX_SIDE_PX, MAX_SIDE_PX))   # hanya mengecilkan, tidak memperbesar
        if img.mode != "RGB":                       # PNG transparan -> latar putih
            bg = Image.new("RGB", img.size, (255, 255, 255))
            alpha = img.convert("RGBA")
            bg.paste(alpha, mask=alpha.split()[-1])
            img = bg
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    except Exception:
        upload.seek(0)
        return upload

    name = Path(upload.name).stem + ".jpg"
    size = buf.tell()
    buf.seek(0)
    return InMemoryUploadedFile(buf, "image", name, "image/jpeg", size, None)


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = [
            'plant_name', 'title', 'category', 'status', 'planting_method',
            'planted_date', 'location', 'content', 'image',
        ]
        widgets = {
            'plant_name': forms.TextInput(attrs={'class': 'in', 'placeholder': 'Contoh: Cabai Rawit'}),
            'title': forms.TextInput(attrs={'class': 'in', 'placeholder': 'Contoh: Daun pertama keluar'}),
            'category': forms.RadioSelect(),
            'status': forms.Select(attrs={'class': 'in'}),
            'planting_method': forms.Select(attrs={'class': 'in'}),
            'planted_date': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'in', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'in', 'placeholder': 'Contoh: Balkon, Jendela Dapur'}),
            'content': forms.Textarea(attrs={'class': 'in', 'rows': 5, 'placeholder': 'Tulis progres atau kejadian penting...'}),
            'image': forms.ClearableFileInput(attrs={'accept': 'image/jpeg,image/png'}),
        }

    # __init__ HARUS sejajar dengan class Meta (bukan di dalam Meta), kalau tidak
    # dijalankan setiap form dibuat, lalu mengubah semua field jadi wajib (required = True) dengan pesan error khusus
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.required = True
            field.error_messages['required'] = f'{REQUIRED_LABELS[name]} wajib diisi.'

    # ---- Pembersihan XSS di sisi server: buang semua tag HTML ----
    def _clean_text(self, field):
        return strip_tags(self.cleaned_data.get(field, '')).strip()

    def clean_plant_name(self):
        value = self._clean_text('plant_name')
        if not value:
            raise forms.ValidationError('Nama tanaman tidak boleh kosong.')
        return value

    def clean_title(self):
        value = self._clean_text('title')
        if not value:
            raise forms.ValidationError('Judul catatan tidak boleh kosong.')
        return value

    def clean_location(self):
        value = self._clean_text('location')
        if not value:
            raise forms.ValidationError('Lokasi tanaman wajib diisi.')
        return value

    def clean_content(self):
        value = self._clean_text('content')
        if not value:
            raise forms.ValidationError('Isi catatan wajib diisi.')
        return value

    def clean_image(self):
        image = self.cleaned_data.get('image')
        # Validasi + perkecil hanya untuk file yang baru diunggah
        if image and hasattr(image, 'content_type'):
            if image.content_type not in ('image/jpeg', 'image/png'):
                raise forms.ValidationError('Format harus JPG atau PNG.')
            if image.size > MAX_IMAGE_MB * 1024 * 1024:
                raise forms.ValidationError(f'Ukuran foto maksimal {MAX_IMAGE_MB} MB.')
            try:
                Image.open(image).verify()          # pastikan benar-benar gambar
            except Exception:
                raise forms.ValidationError('File bukan gambar yang valid.')
            image.seek(0)
            return shrink_image(image)
        return image
    
    # User kirim form
   #Django cek semua field wajib terisi         (__init__)
   # bersihkan teks, buang tag HTML              (clean_title, dst.)
   # cek foto: tipe, ukuran, benar-benar gambar  (clean_image)
   # perkecil foto jadi JPEG                     (shrink_image)
   # kalau lolos semua → view menyimpan ke database
   # kalau ada yang gagal → error tampil di form / toast