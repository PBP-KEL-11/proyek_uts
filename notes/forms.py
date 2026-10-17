from django import forms
from .models import Note

MAX_IMAGE_MB = 2


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

    def clean_image(self):
        image = self.cleaned_data.get('image')
        # Validasi hanya untuk file yang baru diunggah
        if image and hasattr(image, 'content_type'):
            if image.content_type not in ('image/jpeg', 'image/png'):
                raise forms.ValidationError('Format harus JPG atau PNG.')
            if image.size > MAX_IMAGE_MB * 1024 * 1024:
                raise forms.ValidationError(f'Ukuran foto maksimal {MAX_IMAGE_MB} MB.')
        return image