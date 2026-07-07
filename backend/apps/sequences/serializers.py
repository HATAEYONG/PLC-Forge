from rest_framework import serializers

from apps.sequences.models import Sequence, SequenceStep


class SequenceStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceStep
        fields = [
            "id",
            "step_no",
            "name",
            "entry_condition",
            "actions",
            "completion_condition",
            "timeout_seconds",
            "timeout_alarm",
            "abort_condition",
            "hold_condition",
            "resume_condition",
            "next_step",
            "fallback_step",
        ]


class SequenceSerializer(serializers.ModelSerializer):
    steps = SequenceStepSerializer(many=True, read_only=True)

    class Meta:
        model = Sequence
        fields = ["id", "project", "decision", "code", "name", "steps", "created_at"]
