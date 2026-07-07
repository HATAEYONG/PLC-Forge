from django.db import models

from core.models import BaseModel


class Interlock(BaseModel):
    """Interlock 정의 (PRD §18)."""

    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="interlocks"
    )
    decision = models.ForeignKey(
        "design.DesignDecision",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interlocks",
    )
    code = models.CharField(max_length=50)
    protected_device = models.CharField(max_length=100, blank=True)
    condition = models.CharField(max_length=255, blank=True)
    effect = models.CharField(max_length=255, blank=True)
    reset_condition = models.CharField(max_length=255, blank=True)
    bypass_allowed = models.BooleanField(default=False)
    bypass_permission = models.CharField(max_length=100, blank=True)
    safety_related = models.BooleanField(default=False)
    reason = models.TextField(blank=True)
    fat_test_required = models.BooleanField(default=True)
    sat_test_required = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(fields=["project", "code"], name="uniq_interlock_per_project")
        ]

    def __str__(self):
        return self.code
