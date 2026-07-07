from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.approvals.models import Approval, ApprovalStatus
from apps.approvals.serializers import (
    ApprovalActionSerializer,
    ApprovalSerializer,
    SubmitReviewSerializer,
)
from apps.approvals.services import submit_for_review, transition_approval
from apps.projects.models import Project


class ApprovalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Approval.objects.prefetch_related("history")
    serializer_class = ApprovalSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    def _transition(self, request, pk, new_status):
        approval = self.get_object()
        serializer = ApprovalActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        approval = transition_approval(
            approval=approval,
            new_status=new_status,
            actor=request.user,
            reason=serializer.validated_data.get("reason", ""),
        )
        return Response(ApprovalSerializer(approval).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        return self._transition(request, pk, ApprovalStatus.APPROVED)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        return self._transition(request, pk, ApprovalStatus.REJECTED)


class SubmitReviewView(viewsets.ViewSet):
    """POST /api/projects/{project_pk}/submit-review/ — 대상을 검토(IN_REVIEW)로 제출."""

    def create(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        serializer = SubmitReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        approval = submit_for_review(
            project=project, target=serializer.validated_data["target"], actor=request.user
        )
        return Response(ApprovalSerializer(approval).data, status=status.HTTP_201_CREATED)
