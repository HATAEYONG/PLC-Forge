from rest_framework import serializers

from apps.validation.models import ValidationFinding


class ValidationFindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationFinding
        fields = [
            "id",
            "project",
            "severity",
            "code",
            "title",
            "description",
            "related_objects",
            "recommended_action",
            "status",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "project",
            "severity",
            "code",
            "title",
            "description",
            "related_objects",
            "recommended_action",
            "created_at",
        ]
