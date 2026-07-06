from rest_framework import serializers

from apps.design.models import DesignDecision, RiskLevel, Rule
from apps.knowledge.models import KnowledgeItem
from apps.projects.models import Project
from apps.requirements.models import ProjectFact


class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = [
            "id",
            "code",
            "version",
            "rule_type",
            "priority",
            "conditions_json",
            "effects_json",
            "explanation_template",
            "severity",
            "confidence",
            "applicable_scope",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DesignDecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignDecision
        fields = [
            "id",
            "project",
            "decision_type",
            "subject_type",
            "subject_id",
            "decision_value_json",
            "reason",
            "input_facts",
            "rules",
            "knowledge_items",
            "confidence",
            "risk_level",
            "approval_required",
            "approval_status",
            "version",
            "created_at",
        ]
        read_only_fields = ["id", "approval_required", "approval_status", "version", "created_at"]


class DesignDecisionCreateSerializer(serializers.Serializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    decision_type = serializers.CharField(max_length=100)
    subject_type = serializers.CharField(
        max_length=100, required=False, allow_blank=True, default=""
    )
    subject_id = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    decision_value = serializers.JSONField()
    reason = serializers.CharField()
    input_facts = serializers.PrimaryKeyRelatedField(
        queryset=ProjectFact.objects.all(), many=True, required=False, default=list
    )
    rules = serializers.PrimaryKeyRelatedField(
        queryset=Rule.objects.all(), many=True, required=False, default=list
    )
    knowledge_items = serializers.PrimaryKeyRelatedField(
        queryset=KnowledgeItem.objects.all(), many=True, required=False, default=list
    )
    confidence = serializers.FloatField(required=False, default=1.0)
    risk_level = serializers.ChoiceField(
        choices=RiskLevel.choices, required=False, default=RiskLevel.LOW
    )
