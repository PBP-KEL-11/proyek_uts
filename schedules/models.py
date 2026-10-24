from django.db import models
from django.conf import settings  
from django.utils import timezone

class PlantTask(models.Model):
    TASK_CHOICES = [
        ('SIRAM', 'Siram Air'),
        ('PUPUK', 'Beri Pupuk'),
        ('POT', 'Ganti Pot'),
        ('PANTAU', 'Cek Hama'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    plant_name = models.CharField(max_length=100)
    task_type = models.CharField(max_length=10, choices=TASK_CHOICES)
    due_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'task_type', 'due_date'], name='unique_task_per_type_per_day'),
        ]

    def mark_as_done(self):
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()

    def __str__(self):
        return f"[{self.get_task_type_display()}] {self.plant_name}"