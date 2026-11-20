from rest_framework import serializers
from plants.models import GardenPlant
from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    category_label = serializers.CharField(source="get_category_display", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    planting_method_label = serializers.CharField(source="get_planting_method_display", read_only=True)

    class Meta:
        model = Note
        fields = [
            "id", "garden_plant", "plant_name", "title",
            "category", "category_label",
            "status", "status_label",
            "planting_method", "planting_method_label",
            "planted_date", "location", "content", "image",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_garden_plant(self, value):
        # hanya boleh menautkan ke tanaman milik sendiri
        if value and value.user != self.context["request"].user:
            raise serializers.ValidationError("Tanaman ini bukan milikmu.")
        return value