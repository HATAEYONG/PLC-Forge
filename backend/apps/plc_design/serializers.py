from rest_framework import serializers

from apps.plc_design.models import PLCCandidate, PLCSizingResult


class PLCCandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PLCCandidate
        fields = ["id", "vendor", "family", "accepted", "reason"]


class PLCSizingResultSerializer(serializers.ModelSerializer):
    candidates = PLCCandidateSerializer(many=True, read_only=True)

    class Meta:
        model = PLCSizingResult
        fields = [
            "id",
            "project",
            "decision",
            "di_count",
            "do_count",
            "ai_count",
            "ao_count",
            "spare_margin_percent",
            "factors_json",
            "required_class",
            "minimum_spec_json",
            "selection_reason",
            "candidates",
            "created_at",
        ]
