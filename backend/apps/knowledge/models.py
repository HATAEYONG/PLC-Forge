from django.conf import settings
from django.db import models

from core.models import BaseModel


class KnowledgeType(models.TextChoices):
    """PRD §11 지식베이스 8개 계층."""

    INDUSTRY = "INDUSTRY", "Industry Knowledge"
    PROCESS = "PROCESS", "Process Knowledge"
    DEVICE = "DEVICE", "Device Knowledge"
    SENSOR = "SENSOR", "Instrument/Sensor Knowledge"
    CONTROL = "CONTROL", "Control Knowledge"
    COMMUNICATION = "COMMUNICATION", "Communication Knowledge"
    HMI_SCADA = "HMI_SCADA", "HMI/SCADA Knowledge"
    FAT_SAT = "FAT_SAT", "FAT/SAT Knowledge"


class ReviewStatus(models.TextChoices):
    DRAFT = "DRAFT", "작성 중"
    IN_REVIEW = "IN_REVIEW", "검토 중"
    APPROVED = "APPROVED", "승인됨"
    REJECTED = "REJECTED", "거절됨"


class KnowledgeItem(BaseModel):
    """PRD §11 KnowledgeItem."""

    code = models.CharField(max_length=100)
    version = models.PositiveIntegerField(default=1)
    knowledge_type = models.CharField(max_length=20, choices=KnowledgeType.choices)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    conditions_json = models.JSONField(default=dict, blank=True)
    recommendations_json = models.JSONField(default=list, blank=True)
    constraints_json = models.JSONField(default=list, blank=True)
    references_json = models.JSONField(default=list, blank=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)
    review_status = models.CharField(
        max_length=10, choices=ReviewStatus.choices, default=ReviewStatus.DRAFT
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["code", "version"], name="uniq_knowledge_code_version")
        ]
        ordering = ["code", "-version"]

    def __str__(self):
        return f"{self.code} v{self.version}"
