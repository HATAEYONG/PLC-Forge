from rest_framework import serializers

from apps.communications.models import CommLink, CommNode, ProtocolRequirement


class CommNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommNode
        fields = ["id", "project", "node_type", "name", "decision", "created_at"]


class CommLinkSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source="source.name", read_only=True)
    target_name = serializers.CharField(source="target.name", read_only=True)

    class Meta:
        model = CommLink
        fields = [
            "id",
            "project",
            "source",
            "target",
            "source_name",
            "target_name",
            "protocol",
            "segment",
            "medium",
            "failure_behavior",
            "comm_alarm",
            "created_at",
        ]


class ProtocolRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProtocolRequirement
        fields = ["id", "project", "requirement", "detail", "created_at"]
