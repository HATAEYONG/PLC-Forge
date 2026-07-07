from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.interlocks.views import CauseEffectView, InterlockViewSet

router = DefaultRouter()
router.register("interlocks", InterlockViewSet)

urlpatterns = [
    *router.urls,
    path(
        "projects/<uuid:project_pk>/cause-effect-matrix/",
        CauseEffectView.as_view({"get": "list"}),
        name="project-cause-effect",
    ),
]
