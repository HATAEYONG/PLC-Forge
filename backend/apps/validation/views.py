from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from apps.projects.models import Project
from apps.validation.engine import run_validation
from apps.validation.models import ValidationFinding
from apps.validation.serializers import ValidationFindingSerializer


class ValidationFindingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Finding 조회 + 상태(ACKNOWLEDGED/RESOLVED/WAIVED) 갱신."""

    queryset = ValidationFinding.objects.all()
    serializer_class = ValidationFindingSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        severity = self.request.query_params.get("severity")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if severity:
            queryset = queryset.filter(severity=severity.upper())
        return queryset


class ValidateView(viewsets.ViewSet):
    """POST /api/projects/{project_pk}/validate/ — 검증 실행."""

    def create(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        summary = run_validation(project)
        return Response(summary, status=status.HTTP_201_CREATED)
