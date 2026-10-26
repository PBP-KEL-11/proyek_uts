from django.forms import ModelForm
from dashboard.models import GreenTrack

class GreenTrackForm():
    class Meta:
        model = GreenTrack
        
        fields=[
            ""
        ]