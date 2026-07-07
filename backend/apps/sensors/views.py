from rest_framework import viewsets

from apps.sensors.models import SensorRequirement
from apps.sensors.serializers import SensorRequirementSerializer


class SensorRequirementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SensorRequirement.objects.prefetch_related("candidates")
    serializer_class = SensorRequirementSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset
