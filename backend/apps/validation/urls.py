from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.validation.views import ValidateView, ValidationFindingViewSet

router = DefaultRouter()
router.register("validation-findings", ValidationFindingViewSet)

urlpatterns = [
    *router.urls,
    path(
        "projects/<uuid:project_pk>/validate/",
        ValidateView.as_view({"post": "create"}),
        name="project-validate",
    ),
]
