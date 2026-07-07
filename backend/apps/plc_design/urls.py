from rest_framework.routers import DefaultRouter

from apps.plc_design.views import PLCSizingResultViewSet

router = DefaultRouter()
router.register("plc-sizing", PLCSizingResultViewSet)

urlpatterns = router.urls
