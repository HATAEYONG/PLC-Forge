from rest_framework.routers import DefaultRouter

from apps.sequences.views import SequenceViewSet

router = DefaultRouter()
router.register("sequences", SequenceViewSet)

urlpatterns = router.urls
