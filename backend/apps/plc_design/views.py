from rest_framework import viewsets

from apps.plc_design.models import PLCSizingResult
from apps.plc_design.serializers import PLCSizingResultSerializer


class PLCSizingResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PLCSizingResult.objects.prefetch_related("candidates")
    serializer_class = PLCSizingResultSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset
