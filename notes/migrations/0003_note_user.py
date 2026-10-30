import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def fill_user_from_garden_plant(apps, schema_editor):
    """Catatan yang terhubung ke GardenPlant mewarisi pemiliknya."""
    Note = apps.get_model('notes', 'Note')
    for note in Note.objects.filter(garden_plant__isnull=False).select_related('garden_plant'):
        note.user_id = note.garden_plant.user_id
        note.save(update_fields=['user'])


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notes', '0002_remove_note_user_note_garden_plant'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='user',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='notes',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(fill_user_from_garden_plant, migrations.RunPython.noop),
    ]