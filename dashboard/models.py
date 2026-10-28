from django.db import models
from django.conf import settings
from plants.models import GardenPlant
# Create your models here.

class GreenTrack(models.Model):
    LEVELS = ["Novice Gardener",
              "Adept Gardener",
              "Botanist",
              "Urban Harvester",
              "Eco Master",
              "Triptolemus",
              "Demeter"]
    
    BADGES = ["Botanis Kecil",
              "Pecinta Alam",
              "Pahlawan Oksigen",
              "Kekasih Alam"
              ]
    
    XPMAX = [250,
             500,
             750,
             1000,
             2000,
             5000]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    current_xp = models.IntegerField(default=0)
    xp_max = models.IntegerField(default=XPMAX[0])
    level_number = models.IntegerField(default=1)
    current_level = models.CharField(default=LEVELS[0])
    active_badge = models.CharField(default="Tidak Ada Badge Aktif")
    streak = models.IntegerField(default=0)
    carbon_absorption = models.FloatField(default=0.0)
    greentrack_nickname = models.CharField(max_length=20, null=True)
    greentrack_description = models.TextField(null=True)