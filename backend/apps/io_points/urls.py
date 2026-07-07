from rest_framework.routers import DefaultRouter

from apps.io_points.views import IOPointViewSet

router = DefaultRouter()
router.register("io-points", IOPointViewSet)

urlpatterns = router.urls
