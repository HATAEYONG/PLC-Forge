from django.db import models

from core.models import BaseModel


class PLCClass(models.TextChoices):
    MICRO = "MICRO", "마이크로/블록형"
    COMPACT = "COMPACT", "컴팩트형"
    MODULAR = "MODULAR", "모듈형(중형)"
    HIGH_END = "HIGH_END", "고성능/이중화"


class PLCSizingResult(BaseModel):
    """PLC Sizing 결과 (PRD §15). I/O 개수만이 아니라 다수 요소를 반영한다."""

    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="plc_sizing_results"
    )
    decision = models.ForeignKey(
        "design.DesignDecision",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="plc_sizing_results",
    )
    di_count = models.PositiveIntegerField(default=0)
    do_count = models.PositiveIntegerField(default=0)
    ai_count = models.PositiveIntegerField(default=0)
    ao_count = models.PositiveIntegerField(default=0)
    spare_margin_percent = models.PositiveIntegerField(default=20)
    # §15 추가 고려 요소
    factors_json = models.JSONField(default=dict, blank=True)
    required_class = models.CharField(max_length=20, choices=PLCClass.choices)
    minimum_spec_json = models.JSONField(default=dict, blank=True)
    selection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"PLC Sizing ({self.required_class})"


class PLCCandidate(BaseModel):
    sizing = models.ForeignKey(PLCSizingResult, on_delete=models.CASCADE, related_name="candidates")
    vendor = models.CharField(max_length=100)
    family = models.CharField(max_length=100, blank=True)
    accepted = models.BooleanField(default=True)
    reason = models.TextField(blank=True)  # Selection Reason / Rejected Reason

    class Meta:
        ordering = ["-accepted", "vendor"]

    def __str__(self):
        status = "채택" if self.accepted else "탈락"
        return f"{self.vendor} {self.family} ({status})"
