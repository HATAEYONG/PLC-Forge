from rest_framework import serializers

from apps.hmi_design.models import HMIScreen, HMITag


class HMITagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HMITag
        fields = ["id", "name", "signal_type", "io_point"]


class HMIScreenSerializer(serializers.ModelSerializer):
    tags = HMITagSerializer(many=True, read_only=True)

    class Meta:
        model = HMIScreen
        fields = [
            "id",
            "project",
            "decision",
            "code",
            "name",
            "purpose",
            "user_role",
            "security_level",
            "required_tags",
            "commands",
            "status_objects",
            "alarm_objects",
            "trend_objects",
            "navigation",
            "order",
            "tags",
            "created_at",
        ]
