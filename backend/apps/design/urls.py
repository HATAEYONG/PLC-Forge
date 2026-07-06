from rest_framework.routers import DefaultRouter

from apps.design.views import DesignDecisionViewSet, RuleViewSet

router = DefaultRouter()
router.register("rules", RuleViewSet)
router.register("design-decisions", DesignDecisionViewSet)

urlpatterns = router.urls
