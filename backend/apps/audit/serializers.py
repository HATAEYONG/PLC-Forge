from rest_framework import serializers

from apps.audit.models import AuditEvent


class AuditEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditEvent
        fields = [
            "id",
            "actor",
            "action",
            "object_type",
            "object_id",
            "before_json",
            "after_json",
            "reason",
            "created_at",
        ]
