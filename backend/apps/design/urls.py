from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.design.views import ApplyRulesView, DesignDecisionViewSet, RuleViewSet

router = DefaultRouter()
router.register("rules", RuleViewSet)
router.register("design-decisions", DesignDecisionViewSet)

urlpatterns = [
    *router.urls,
    path(
        "projects/<uuid:project_pk>/apply-rules/",
        ApplyRulesView.as_view({"post": "create"}),
        name="project-apply-rules",
    ),
]
