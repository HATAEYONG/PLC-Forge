from rest_framework import viewsets

from apps.hmi_design.models import HMIScreen
from apps.hmi_design.serializers import HMIScreenSerializer


class HMIScreenViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HMIScreen.objects.prefetch_related("tags")
    serializer_class = HMIScreenSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset
