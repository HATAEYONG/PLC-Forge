from rest_framework import serializers

from apps.alarms.models import Alarm


class AlarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alarm
        fields = [
            "id",
            "project",
            "decision",
            "code",
            "source",
            "condition",
            "delay_seconds",
            "priority",
            "message",
            "operator_action",
            "reset_type",
            "latching",
            "related_interlock",
            "fat_test_required",
            "sat_test_required",
            "created_at",
        ]
