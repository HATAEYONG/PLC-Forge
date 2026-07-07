from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.design import orchestrator, rule_engine, services
from apps.design.models import DesignDecision, Rule
from apps.design.serializers import (
    DesignDecisionCreateSerializer,
    DesignDecisionSerializer,
    RuleSerializer,
)
from apps.projects.models import Project


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

    @action(detail=True, methods=["post"])
    def override(self, request, pk=None):
        decision = self.get_object()
        decision = rule_engine.override_decision(
            decision=decision, actor=request.user, reason=request.data.get("reason", "")
        )
        return Response(DesignDecisionSerializer(decision).data)


class ApplyRulesView(viewsets.ViewSet):
    """POST /api/projects/{project_pk}/apply-rules/ — 규칙 엔진 실행."""

    def create(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        result = rule_engine.apply_rules(project=project, actor=request.user)
        return Response(
            {
                "matched_rules": result["matched_rules"],
                "decisions": DesignDecisionSerializer(result["decisions"], many=True).data,
                "conflicts": result["conflicts"],
            },
            status=status.HTTP_201_CREATED,
        )


class GenerateDesignView(viewsets.ViewSet):
    """POST /api/projects/{project_pk}/generate-design/?stage=sensor|io|plc|all"""

    def create(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        stage = request.query_params.get("stage", "all")
        summary = orchestrator.generate_design(project=project, stage=stage, actor=request.user)
        return Response({"stage": stage, "summary": summary}, status=status.HTTP_201_CREATED)
