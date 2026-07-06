from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from rest_framework import serializers

from apps.interview.models import AnswerOption, InterviewAnswer, InterviewSession, Question


class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = ["id", "question", "value", "label", "order"]
        read_only_fields = ["id"]


class QuestionSerializer(serializers.ModelSerializer):
    options = AnswerOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "code",
            "version",
            "text",
            "help_text",
            "category",
            "question_type",
            "answer_schema",
            "priority",
            "criticality",
            "required_conditions",
            "exclusion_conditions",
            "applicable_industries",
            "applicable_processes",
            "unlocks_facts",
            "unlocks_decisions",
            "risk_detection_tags",
            "is_active",
            "options",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_answer_schema(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("answer_schema는 JSON 객체여야 합니다.")
        try:
            Draft202012Validator.check_schema(value)
        except SchemaError as exc:
            raise serializers.ValidationError(
                f"answer_schema가 유효한 JSON Schema가 아닙니다: {exc.message}"
            ) from exc
        return value


class InterviewSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewSession
        fields = ["id", "project", "status", "started_by", "completed_at", "created_at"]
        read_only_fields = ["id", "status", "started_by", "completed_at", "created_at"]


class InterviewAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewAnswer
        fields = ["id", "session", "question", "raw_answer", "answered_by", "created_at"]
        read_only_fields = ["id", "session", "answered_by", "created_at"]


class AnswerSubmitSerializer(serializers.Serializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.filter(is_active=True))
    raw_answer = serializers.JSONField()
