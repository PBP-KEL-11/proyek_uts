from rest_framework.routers import DefaultRouter
from .api_views import GreentrackViewSet

router = DefaultRouter()
router.register("", GreentrackViewSet, basename="greentrack-api")

urlpatterns = router.urls