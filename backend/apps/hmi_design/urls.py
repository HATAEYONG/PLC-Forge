from rest_framework.routers import DefaultRouter

from apps.hmi_design.views import HMIScreenViewSet

router = DefaultRouter()
router.register("hmi-screens", HMIScreenViewSet)

urlpatterns = router.urls
