from rest_framework import serializers

from apps.fat_sat.models import TestCase


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = [
            "id",
            "project",
            "phase",
            "test_id",
            "category",
            "precondition",
            "procedure",
            "expected_result",
            "actual_result",
            "status",
            "evidence",
            "tester",
            "reviewer",
            "source_type",
            "source_ref",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "project",
            "phase",
            "test_id",
            "category",
            "precondition",
            "procedure",
            "expected_result",
            "source_type",
            "source_ref",
            "created_at",
        ]
