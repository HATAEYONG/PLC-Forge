from rest_framework.routers import DefaultRouter

from apps.communications.views import (
    CommLinkViewSet,
    CommNodeViewSet,
    ProtocolRequirementViewSet,
)

router = DefaultRouter()
router.register("comm-nodes", CommNodeViewSet)
router.register("comm-links", CommLinkViewSet)
router.register("protocol-requirements", ProtocolRequirementViewSet)

urlpatterns = router.urls
