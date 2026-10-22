from django.contrib import admin
from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'plant_name', 'category', 'status', 'user', 'planted_date')
    list_filter = ('category', 'status')
    search_fields = ('title', 'plant_name', 'location')