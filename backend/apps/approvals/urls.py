from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.approvals.views import ApprovalViewSet, SubmitReviewView

router = DefaultRouter()
router.register("approvals", ApprovalViewSet)

urlpatterns = [
    *router.urls,
    path(
        "projects/<uuid:project_pk>/submit-review/",
        SubmitReviewView.as_view({"post": "create"}),
        name="project-submit-review",
    ),
]
