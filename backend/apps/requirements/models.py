from django.db import models

from core.models import BaseModel


class FactStatus(models.TextChoices):
    """PRD §10 FactStatus."""

    PROPOSED = "PROPOSED", "제안됨"
    CONFIRMED = "CONFIRMED", "확정됨"
    CONFLICTED = "CONFLICTED", "충돌"
    SUPERSEDED = "SUPERSEDED", "대체됨"
    REJECTED = "REJECTED", "거절됨"


class ValueType(models.TextChoices):
    STRING = "STRING", "문자열"
    NUMBER = "NUMBER", "숫자"
    BOOLEAN = "BOOLEAN", "불리언"
    LIST = "LIST", "목록"
    OBJECT = "OBJECT", "객체"


class SourceType(models.TextChoices):
    ANSWER = "ANSWER", "인터뷰 답변"
    RULE = "RULE", "규칙 적용"
    LLM = "LLM", "LLM 구조화"
    MANUAL = "MANUAL", "수동 입력"


class ProjectFact(BaseModel):
    """PRD §10 ProjectFact. ProjectState는 이 모델의 Projection으로 계산한다."""

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="facts")
    fact_key = models.CharField(max_length=255)
    value_json = models.JSONField()
    value_type = models.CharField(max_length=10, choices=ValueType.choices)
    unit = models.CharField(max_length=50, blank=True)
    source_type = models.CharField(
        max_length=10, choices=SourceType.choices, default=SourceType.MANUAL
    )
    source_answer = models.ForeignKey(
        "interview.InterviewAnswer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="facts",
    )
    confidence = models.FloatField(default=1.0)
    status = models.CharField(
        max_length=10, choices=FactStatus.choices, default=FactStatus.PROPOSED
    )
    version = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "fact_key", "version"], name="uniq_fact_key_version"
            )
        ]
        indexes = [models.Index(fields=["project", "fact_key"])]
        ordering = ["fact_key", "-version"]

    def __str__(self):
        return f"{self.fact_key} v{self.version} ({self.status})"
