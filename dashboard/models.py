from django.db import models
from django.conf import settings
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
    greentrack_nickname = models.CharField(max_length=20, null=True)
    greentrack_description = models.TextField(null=True)
        
    def level_up(self):
        if self.current_level != self.LEVELS[6]:
            self.current_level = self.LEVEL[self.current_level]
            self.xp_max = self.XPMAX[self.current_level]
            self.current_level+=1
            
    def add_xp(self):
        self.current_xp+=100;
        if self.current_xp>=self.xp_max:
            self.level_up()
            
        if self.current_level == 1 and self.current_xp == 200:
            self.active_badge = self.BADGES[0]
            
        if self.current_level == 2 and self.current_xp == 400:
                    self.active_badge = self.BADGES[1]
                    
        if self.current_level == 4 and self.current_xp == 900:
                    self.active_badge = self.BADGES[2]
                    
        if self.current_level == 6 and self.current_xp == 1500:
                    self.active_badge = self.BADGES[3]
        
            
            
    