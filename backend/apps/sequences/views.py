from rest_framework import viewsets

from apps.sequences.models import Sequence
from apps.sequences.serializers import SequenceSerializer


class SequenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Sequence.objects.prefetch_related("steps")
    serializer_class = SequenceSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset
