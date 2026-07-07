from rest_framework.routers import DefaultRouter

from apps.fat_sat.views import TestCaseViewSet

router = DefaultRouter()
router.register("test-cases", TestCaseViewSet)

urlpatterns = router.urls
