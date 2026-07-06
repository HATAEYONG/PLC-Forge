from rest_framework import serializers

from apps.knowledge.models import KnowledgeItem


class KnowledgeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeItem
        fields = [
            "id",
            "code",
            "version",
            "knowledge_type",
            "title",
            "description",
            "conditions_json",
            "recommendations_json",
            "constraints_json",
            "references_json",
            "valid_from",
            "valid_to",
            "review_status",
            "reviewed_by",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
