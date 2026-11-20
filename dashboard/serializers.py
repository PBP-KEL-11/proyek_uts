from rest_framework import serializers
from plants.models import GardenPlant
from .models import GreenTrack


class GreentrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = GreenTrack
        fields = [
            "user",
            "current_xp",
            "xp_max",
            "level_number",
            "current_level",
            "active_badge",
            "greentrack_nickname",
            "greentrack_description"
        ]
        read_only_fields = ["user"]
        
        def validate_greentrack(self, value):
            if value and value.user != self.context["request"].user:
                raise serializers.ValidationError("Greentrack ini bukan milikmu")
            return value