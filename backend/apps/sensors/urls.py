from rest_framework.routers import DefaultRouter

from apps.sensors.views import SensorRequirementViewSet

router = DefaultRouter()
router.register("sensor-requirements", SensorRequirementViewSet)

urlpatterns = router.urls
