from rest_framework import serializers

from apps.sensors.models import SensorCandidate, SensorRequirement


class SensorCandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorCandidate
        fields = ["id", "vendor", "model", "rationale", "rejected", "reject_reason"]


class SensorRequirementSerializer(serializers.ModelSerializer):
    candidates = SensorCandidateSerializer(many=True, read_only=True)

    class Meta:
        model = SensorRequirement
        fields = [
            "id",
            "project",
            "decision",
            "measurement_type",
            "measurement_principle",
            "sensor_technology",
            "signal_type",
            "accuracy",
            "range_text",
            "response_time",
            "material_compatibility",
            "environmental_rating",
            "installation_constraints",
            "maintenance_requirements",
            "communication_requirements",
            "is_continuous",
            "candidates",
            "created_at",
        ]
