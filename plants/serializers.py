from rest_framework import serializers

from .models import GardenPlant, Plant


class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = [
            "id",
            "species_id",
            "common_name",
            "scientific_name",
            "thumbnail",
            "watering",
            "watering_days",
            "sunlight",
        ]
        read_only_fields = ["id"]


class GardenPlantSerializer(serializers.ModelSerializer):
    plant_detail = PlantSerializer(source="plant", read_only=True)
    next_watering = serializers.DateTimeField(read_only=True)
    needs_water = serializers.BooleanField(read_only=True)

    class Meta:
        model = GardenPlant
        fields = [
            "id",
            "plant",
            "plant_detail",
            "nickname",
            "notes",
            "last_watered",
            "added_at",
            "next_watering",
            "needs_water",
        ]
        read_only_fields = ["id", "added_at"]

    def validate_plant(self, value):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            qs = GardenPlant.objects.filter(user=request.user, plant=value)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError("Tanaman ini sudah ada di kebunmu.")
        return value
