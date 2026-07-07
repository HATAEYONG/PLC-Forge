from django.db import models

from core.models import BaseModel


class SecurityLevel(models.TextChoices):
    OPERATOR = "OPERATOR", "운전자"
    SUPERVISOR = "SUPERVISOR", "관리자"
    ENGINEER = "ENGINEER", "엔지니어"


class HMIScreen(BaseModel):
    """HMI 화면 정의 (PRD §17). 설계 상태에 따라 필요한 화면만 생성한다."""

    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="hmi_screens"
    )
    decision = models.ForeignKey(
        "design.DesignDecision",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hmi_screens",
    )
    code = models.CharField(max_length=50)  # MAIN_OVERVIEW, ALARM_SUMMARY, ...
    name = models.CharField(max_length=100)
    purpose = models.CharField(max_length=255, blank=True)
    user_role = models.CharField(
        max_length=20, choices=SecurityLevel.choices, default=SecurityLevel.OPERATOR
    )
    security_level = models.CharField(
        max_length=20, choices=SecurityLevel.choices, default=SecurityLevel.OPERATOR
    )
    required_tags = models.JSONField(default=list, blank=True)
    commands = models.JSONField(default=list, blank=True)
    status_objects = models.JSONField(default=list, blank=True)
    alarm_objects = models.JSONField(default=list, blank=True)
    trend_objects = models.JSONField(default=list, blank=True)
    navigation = models.JSONField(default=list, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["project", "code"], name="uniq_hmi_screen_per_project")
        ]

    def __str__(self):
        return self.name


class HMITag(BaseModel):
    screen = models.ForeignKey(HMIScreen, on_delete=models.CASCADE, related_name="tags")
    name = models.CharField(max_length=100)
    signal_type = models.CharField(max_length=10, blank=True)
    io_point = models.ForeignKey(
        "io_points.IOPoint",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hmi_tags",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
