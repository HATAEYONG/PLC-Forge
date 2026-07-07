from django.db import models

from core.models import BaseModel


class Sequence(BaseModel):
    """Vendor Independent 시퀀스 (PRD §19). IR로 먼저 생성한다."""

    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="sequences"
    )
    decision = models.ForeignKey(
        "design.DesignDecision",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sequences",
    )
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(fields=["project", "code"], name="uniq_sequence_per_project")
        ]

    def __str__(self):
        return self.name


class SequenceStep(BaseModel):
    """Sequence Step (PRD §19)."""

    sequence = models.ForeignKey(Sequence, on_delete=models.CASCADE, related_name="steps")
    step_no = models.PositiveIntegerField()
    name = models.CharField(max_length=100)
    entry_condition = models.CharField(max_length=255, blank=True)
    actions = models.JSONField(default=list, blank=True)
    completion_condition = models.CharField(max_length=255, blank=True)
    timeout_seconds = models.FloatField(null=True, blank=True)
    timeout_alarm = models.CharField(max_length=50, blank=True)
    abort_condition = models.CharField(max_length=255, blank=True)
    hold_condition = models.CharField(max_length=255, blank=True)
    resume_condition = models.CharField(max_length=255, blank=True)
    next_step = models.PositiveIntegerField(null=True, blank=True)
    fallback_step = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["sequence", "step_no"]
        constraints = [
            models.UniqueConstraint(
                fields=["sequence", "step_no"], name="uniq_step_no_per_sequence"
            )
        ]

    def __str__(self):
        return f"{self.step_no}. {self.name}"
