from django.db import models

from core.models import BaseModel


class SignalType(models.TextChoices):
    DI = "DI", "디지털 입력"
    DO = "DO", "디지털 출력"
    AI = "AI", "아날로그 입력"
    AO = "AO", "아날로그 출력"


class IOPoint(BaseModel):
    """I/O List 항목 (PRD §13 I/O Design)."""

    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="io_points"
    )
    decision = models.ForeignKey(
        "design.DesignDecision",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="io_points",
    )
    tag = models.CharField(max_length=100)
    signal_type = models.CharField(max_length=10, choices=SignalType.choices)
    description = models.CharField(max_length=255, blank=True)
    source_type = models.CharField(max_length=20, blank=True)  # DEVICE / SENSOR
    source_ref = models.CharField(max_length=100, blank=True)
    sensor_requirement = models.ForeignKey(
        "sensors.SensorRequirement",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="io_points",
    )

    class Meta:
        ordering = ["signal_type", "tag"]
        constraints = [
            models.UniqueConstraint(fields=["project", "tag"], name="uniq_io_tag_per_project")
        ]

    def __str__(self):
        return f"{self.tag} ({self.signal_type})"
