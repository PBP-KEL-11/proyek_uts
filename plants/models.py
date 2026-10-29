from datetime import timedelta
from django.conf import settings
from django.db import models
from django.utils import timezone


# plants/models.py

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Plant(models.Model):
    species_id = models.PositiveIntegerField(unique=True)
    common_name = models.CharField(max_length=200)
    scientific_name = models.CharField(max_length=200, blank=True)
    thumbnail = models.URLField(max_length=500, blank=True)
    watering = models.CharField(max_length=50, blank=True)
    watering_days = models.PositiveSmallIntegerField(default=7)
    sunlight = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.common_name


class GardenPlant(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="garden",
    )
    plant = models.ForeignKey(
        Plant,
        on_delete=models.PROTECT,
        related_name="owners",
    )
    nickname = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    last_watered = models.DateTimeField(default=timezone.now)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "plant"],
                name="unique_user_garden_plant",
            )
        ]
        ordering = ["-added_at"]

    @property
    def next_watering(self):
        return self.last_watered + timedelta(
            days=self.plant.watering_days
        )

    @property
    def needs_water(self):
        return timezone.now() >= self.next_watering

    def __str__(self):
        return f"{self.user} - {self.plant}"