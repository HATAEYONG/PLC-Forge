from rest_framework import viewsets

from apps.io_points.models import IOPoint
from apps.io_points.serializers import IOPointSerializer


class IOPointViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IOPoint.objects.all()
    serializer_class = IOPointSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset
