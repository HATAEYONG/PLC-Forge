from django.conf import settings
from django.db import models

from core.models import BaseModel


class ApprovalTarget(models.TextChoices):
    """PRD §23 Approval 대상."""

    REQUIREMENT_BASELINE = "REQUIREMENT_BASELINE", "요구사항 Baseline"
    SENSOR_DESIGN = "SENSOR_DESIGN", "센서 설계"
    PLC_DESIGN = "PLC_DESIGN", "PLC 설계"
    COMMUNICATION_DESIGN = "COMMUNICATION_DESIGN", "통신 설계"
    HMI_DESIGN = "HMI_DESIGN", "HMI 설계"
    ALARM_INTERLOCK_DESIGN = "ALARM_INTERLOCK_DESIGN", "알람/인터록 설계"
    SEQUENCE_DESIGN = "SEQUENCE_DESIGN", "시퀀스 설계"
    FAT_PLAN = "FAT_PLAN", "FAT 계획"
    SAT_PLAN = "SAT_PLAN", "SAT 계획"
    VENDOR_CODE_GENERATION = "VENDOR_CODE_GENERATION", "벤더 코드 생성"
    AS_BUILT_RELEASE = "AS_BUILT_RELEASE", "As-Built 릴리스"


class ApprovalStatus(models.TextChoices):
    DRAFT = "DRAFT", "작성 중"
    IN_REVIEW = "IN_REVIEW", "검토 중"
    APPROVED = "APPROVED", "승인됨"
    REJECTED = "REJECTED", "거절됨"
    SUPERSEDED = "SUPERSEDED", "대체됨"


# Safety 관련 승인 대상 (승인 없이 확정 불가, PRD §3.5)
SAFETY_TARGETS = {
    ApprovalTarget.ALARM_INTERLOCK_DESIGN,
    ApprovalTarget.VENDOR_CODE_GENERATION,
}

# Vendor 생성 등 CRITICAL 차단 게이트가 적용되는 대상 (§22)
GENERATION_TARGETS = {ApprovalTarget.VENDOR_CODE_GENERATION, ApprovalTarget.AS_BUILT_RELEASE}


class Approval(BaseModel):
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="approvals"
    )
    target = models.CharField(max_length=30, choices=ApprovalTarget.choices)
    status = models.CharField(
        max_length=12, choices=ApprovalStatus.choices, default=ApprovalStatus.DRAFT
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ["target"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "target"],
                condition=models.Q(status__in=["DRAFT", "IN_REVIEW", "APPROVED"]),
                name="uniq_active_approval_per_target",
            )
        ]

    def __str__(self):
        return f"{self.target} ({self.status})"


class ApprovalHistory(BaseModel):
    approval = models.ForeignKey(Approval, on_delete=models.CASCADE, related_name="history")
    from_status = models.CharField(max_length=12)
    to_status = models.CharField(max_length=12)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ["created_at"]
