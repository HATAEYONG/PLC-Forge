from rest_framework import serializers

from apps.interlocks.models import Interlock


class InterlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interlock
        fields = [
            "id",
            "project",
            "decision",
            "code",
            "protected_device",
            "condition",
            "effect",
            "reset_condition",
            "bypass_allowed",
            "bypass_permission",
            "safety_related",
            "reason",
            "fat_test_required",
            "sat_test_required",
            "created_at",
        ]
