from rest_framework.routers import DefaultRouter

from .api_views import GardenPlantViewSet, PlantViewSet

router = DefaultRouter()
router.register("garden", GardenPlantViewSet, basename="garden-plant-api")
router.register("", PlantViewSet, basename="plant-api")

urlpatterns = router.urls
