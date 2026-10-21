from django.db import models
from authentication.models import User
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    current_xp = models.IntegerField(default=0)
    xp_max = models.IntegerField(default=XPMAX[0])
    level_number = models.IntegerField(default=1)
    current_level = models.CharField(default=LEVELS[0])
    active_badge = models.CharField(default="Tidak Ada Badge Aktif")
    streak = models.IntegerField(default=0)
    carbon_absorption = models.FloatField(default=0.0)

