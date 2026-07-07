from rest_framework import serializers

from apps.io_points.models import IOPoint


class IOPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = IOPoint
        fields = [
            "id",
            "project",
            "decision",
            "tag",
            "signal_type",
            "description",
            "source_type",
            "source_ref",
            "sensor_requirement",
            "created_at",
        ]
