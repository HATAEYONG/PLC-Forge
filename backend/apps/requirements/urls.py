from rest_framework.routers import DefaultRouter

from apps.requirements.views import ProjectFactViewSet

router = DefaultRouter()
router.register("facts", ProjectFactViewSet)

urlpatterns = router.urls
