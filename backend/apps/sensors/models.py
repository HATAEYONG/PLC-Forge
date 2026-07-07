from django.db import models

from core.models import BaseModel


class SignalType(models.TextChoices):
    DI = "DI", "디지털 입력"
    DO = "DO", "디지털 출력"
    AI = "AI", "아날로그 입력"
    AO = "AO", "아날로그 출력"


class SensorRequirement(BaseModel):
    """센서 설계 (PRD §14). 특정 제조사 모델을 바로 선택하지 않고 요구사항을 먼저 정의한다."""

    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="sensor_requirements"
    )
    # PRD §13: 근거·추적은 DesignDecision으로 단일화한다.
    decision = models.ForeignKey(
        "design.DesignDecision",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sensor_requirements",
    )
    measurement_type = models.CharField(max_length=50)  # LEVEL, TEMPERATURE, ...
    # §14 파이프라인 단계
    measurement_principle = models.CharField(max_length=50, blank=True)  # RADAR, RTD, ...
    sensor_technology = models.CharField(max_length=100, blank=True)
    signal_type = models.CharField(max_length=10, choices=SignalType.choices, blank=True)
    accuracy = models.CharField(max_length=50, blank=True)
    range_text = models.CharField(max_length=100, blank=True)
    response_time = models.CharField(max_length=50, blank=True)
    material_compatibility = models.CharField(max_length=200, blank=True)
    environmental_rating = models.CharField(max_length=50, blank=True)
    installation_constraints = models.TextField(blank=True)
    maintenance_requirements = models.TextField(blank=True)
    communication_requirements = models.CharField(max_length=100, blank=True)
    is_continuous = models.BooleanField(default=True)

    class Meta:
        ordering = ["measurement_type"]
        indexes = [models.Index(fields=["project", "measurement_type"])]

    def __str__(self):
        return f"{self.measurement_type} → {self.measurement_principle or '미정'}"


class SensorCandidate(BaseModel):
    """센서 후보 (§14 마지막 단계 Vendor Candidate). Vendor Independent 이후 단계."""

    requirement = models.ForeignKey(
        SensorRequirement, on_delete=models.CASCADE, related_name="candidates"
    )
    vendor = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    rationale = models.TextField(blank=True)
    rejected = models.BooleanField(default=False)
    reject_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["rejected", "vendor"]

    def __str__(self):
        return f"{self.vendor} {self.model}".strip()
