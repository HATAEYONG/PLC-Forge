from rest_framework.routers import DefaultRouter

from apps.alarms.views import AlarmViewSet

router = DefaultRouter()
router.register("alarms", AlarmViewSet)

urlpatterns = router.urls
