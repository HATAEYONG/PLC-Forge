from rest_framework import viewsets

from apps.communications.models import CommLink, CommNode, ProtocolRequirement
from apps.communications.serializers import (
    CommLinkSerializer,
    CommNodeSerializer,
    ProtocolRequirementSerializer,
)


class _ProjectScopedReadViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset


class CommNodeViewSet(_ProjectScopedReadViewSet):
    queryset = CommNode.objects.all()
    serializer_class = CommNodeSerializer


class CommLinkViewSet(_ProjectScopedReadViewSet):
    queryset = CommLink.objects.select_related("source", "target")
    serializer_class = CommLinkSerializer


class ProtocolRequirementViewSet(_ProjectScopedReadViewSet):
    queryset = ProtocolRequirement.objects.all()
    serializer_class = ProtocolRequirementSerializer
