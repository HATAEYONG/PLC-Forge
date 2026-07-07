from django.db import models

from core.models import BaseModel


class AlarmPriority(models.TextChoices):
    LOW = "LOW", "낮음"
    MEDIUM = "MEDIUM", "보통"
    HIGH = "HIGH", "높음"
    CRITICAL = "CRITICAL", "치명적"


class ResetType(models.TextChoices):
    AUTO = "AUTO", "자동 복귀"
    MANUAL = "MANUAL", "수동 복귀"


class Alarm(BaseModel):
    """Alarm 정의 (PRD §18)."""

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="alarms")
    decision = models.ForeignKey(
        "design.DesignDecision",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alarms",
    )
    code = models.CharField(max_length=50)
    source = models.CharField(max_length=100, blank=True)
    condition = models.CharField(max_length=255, blank=True)
    delay_seconds = models.FloatField(default=0)
    priority = models.CharField(
        max_length=10, choices=AlarmPriority.choices, default=AlarmPriority.MEDIUM
    )
    message = models.CharField(max_length=255, blank=True)
    operator_action = models.TextField(blank=True)
    reset_type = models.CharField(max_length=10, choices=ResetType.choices, default=ResetType.AUTO)
    latching = models.BooleanField(default=False)
    related_interlock = models.CharField(max_length=50, blank=True)
    fat_test_required = models.BooleanField(default=True)
    sat_test_required = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(fields=["project", "code"], name="uniq_alarm_per_project")
        ]

    def __str__(self):
        return self.code
