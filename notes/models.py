# notes/models.py

from django.conf import settings
from django.db import models
from django.utils import timezone


class Note(models.Model):
    class Category(models.TextChoices):
        SAYUR = "sayur", "Sayur"
        BUMBU = "bumbu", "Bumbu Dapur"
        HERBAL = "herbal", "Herbal"
        BUNGA = "bunga", "Bunga"
        BUAH = "buah", "Buah"
        LAINNYA = "lainnya", "Lainnya"

    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        SEEDED = "seeded", "Seeded"
        GROWING = "growing", "Growing"
        HARVESTING = "harvesting", "Harvesting"
        DONE = "done", "Done"

    class Method(models.TextChoices):
        DIRECT_SOW = "direct_sow", "Direct Sow"
        INDOOR_START = "indoor_start", "Indoor Start"
        TRANSPLANT = "transplant", "Transplant"

    
    garden_plant = models.ForeignKey(
    "plants.GardenPlant",
    on_delete=models.CASCADE,
    related_name="journal_entries",
    null=True,
    blank=True,
)

    plant_name = models.CharField(max_length=100)
    title = models.CharField(max_length=150)

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.SAYUR,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
    )
    planting_method = models.CharField(
        max_length=20,
        choices=Method.choices,
        default=Method.DIRECT_SOW,
    )

    planted_date = models.DateField(default=timezone.localdate)
    location = models.CharField(max_length=100, blank=True)
    content = models.TextField(blank=True)
    image = models.ImageField(
        upload_to="notes/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def user(self):
        return self.garden_plant.user

    def __str__(self):
        return f"{self.title} ({self.plant_name})"