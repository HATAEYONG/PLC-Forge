from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response

from apps.interlocks.models import Interlock
from apps.interlocks.serializers import InterlockSerializer
from apps.interlocks.services import cause_effect_matrix
from apps.projects.models import Project


class InterlockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Interlock.objects.all()
    serializer_class = InterlockSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset


class CauseEffectView(viewsets.ViewSet):
    """GET /api/projects/{project_pk}/cause-effect-matrix/ (PRD §18)."""

    def list(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        return Response(cause_effect_matrix(project=project))
