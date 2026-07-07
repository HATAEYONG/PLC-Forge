from rest_framework import serializers

from apps.approvals.models import Approval, ApprovalHistory, ApprovalTarget


class ApprovalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalHistory
        fields = ["id", "from_status", "to_status", "actor", "reason", "created_at"]


class ApprovalSerializer(serializers.ModelSerializer):
    history = ApprovalHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Approval
        fields = [
            "id",
            "project",
            "target",
            "status",
            "approver",
            "reason",
            "history",
            "created_at",
        ]
        read_only_fields = ["id", "status", "approver", "history", "created_at"]


class SubmitReviewSerializer(serializers.Serializer):
    target = serializers.ChoiceField(choices=ApprovalTarget.choices)


class ApprovalActionSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, default="")
