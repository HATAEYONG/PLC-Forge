from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from apps.design import services
from apps.design.models import DesignDecision, Rule
from apps.design.serializers import (
    DesignDecisionCreateSerializer,
    DesignDecisionSerializer,
    RuleSerializer,
)


class RuleViewSet(viewsets.ModelViewSet):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer


class DesignDecisionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = DesignDecision.objects.prefetch_related("input_facts", "rules", "knowledge_items")
    serializer_class = DesignDecisionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = DesignDecisionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        decision = services.create_design_decision(**serializer.validated_data, actor=request.user)
        return Response(DesignDecisionSerializer(decision).data, status=status.HTTP_201_CREATED)
