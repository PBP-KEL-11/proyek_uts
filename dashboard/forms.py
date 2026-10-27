from django.forms import ModelForm
from django.forms import ModelForm, TextInput, Textarea
from dashboard.models import GreenTrack

class GreenTrackForm(ModelForm):
    class Meta:
        model = GreenTrack
        
        fields=[
            "greentrack_nickname",
            "greentrack_description",
        ]
        
        labels={
            "greentrack_nickname":"Nama Green Track",
            "greentrack_description":"Deskripsi Green Track",
        }
        
        widgets={
            "greentrack_nickname": TextInput(
                attrs={
                    "placeholder": "Nama kamu untuk Green Track",
                    "maxlength": 20,
                }
            ),
            "greentrack_description": Textarea(
                attrs={
                    "placeholder": "Jelaskan Alasan atau Ketertarikanmu kepada Jejak Hijaumu!",
                }
            ),
        }