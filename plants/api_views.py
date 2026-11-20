from django.db.models import ProtectedError, Q
from rest_framework import permissions, viewsets
from rest_framework.exceptions import ValidationError

from main.api_auth import CsrfExemptSessionAuthentication

from .models import GardenPlant, Plant
from .serializers import GardenPlantSerializer, PlantSerializer


class PlantViewSet(viewsets.ModelViewSet):
    serializer_class = PlantSerializer
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Plant.objects.all()
        q = self.request.query_params.get("q")
        watering = self.request.query_params.get("watering")
        sunlight = self.request.query_params.get("sunlight")

        if q:
            qs = qs.filter(
                Q(common_name__icontains=q) | Q(scientific_name__icontains=q)
            )
        if watering:
            qs = qs.filter(watering__iexact=watering)
        if sunlight:
            qs = qs.filter(sunlight__icontains=sunlight)
        return qs

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError("Tanaman ini masih dipakai di kebun pengguna.")


class GardenPlantViewSet(viewsets.ModelViewSet):
    serializer_class = GardenPlantSerializer
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = GardenPlant.objects.filter(user=self.request.user).select_related("plant")
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(
                Q(plant__common_name__icontains=q) | Q(nickname__icontains=q)
            )
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
