from rest_framework import serializers

from apps.requirements.models import FactStatus, ProjectFact


class ProjectFactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFact
        fields = [
            "id",
            "project",
            "fact_key",
            "value_json",
            "value_type",
            "unit",
            "source_type",
            "source_answer",
            "confidence",
            "status",
            "version",
            "created_at",
        ]
        read_only_fields = ["id", "status", "version", "created_at"]


class FactTransitionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=FactStatus.choices)
    reason = serializers.CharField(required=False, allow_blank=True, default="")
