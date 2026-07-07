from django.db import models

from core.models import BaseModel


class Severity(models.TextChoices):
    INFO = "INFO", "정보"
    WARNING = "WARNING", "경고"
    ERROR = "ERROR", "오류"
    CRITICAL = "CRITICAL", "치명적"


class FindingStatus(models.TextChoices):
    OPEN = "OPEN", "미해결"
    ACKNOWLEDGED = "ACKNOWLEDGED", "확인됨"
    RESOLVED = "RESOLVED", "해결됨"
    WAIVED = "WAIVED", "예외 승인"


class ValidationFinding(BaseModel):
    """검증 결과 항목 (PRD §22)."""

    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="validation_findings"
    )
    severity = models.CharField(max_length=10, choices=Severity.choices)
    code = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    related_objects = models.JSONField(default=list, blank=True)
    recommended_action = models.TextField(blank=True)
    status = models.CharField(
        max_length=15, choices=FindingStatus.choices, default=FindingStatus.OPEN
    )

    class Meta:
        ordering = ["severity", "code"]
        indexes = [models.Index(fields=["project", "severity"])]

    def __str__(self):
        return f"[{self.severity}] {self.code}"
