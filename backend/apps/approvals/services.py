"""Approval Workflow (PRD §23).

상태기계: DRAFT → IN_REVIEW → APPROVED | REJECTED. REJECTED → DRAFT(재작업).
건너뛰기 전이는 거부한다. Vendor 생성 등 GENERATION_TARGETS 승인은 CRITICAL 검증
차단 게이트를 통과해야 한다 (§22, §33-14).
"""

from django.db import transaction

from apps.approvals.models import (
    GENERATION_TARGETS,
    Approval,
    ApprovalHistory,
    ApprovalStatus,
)
from apps.audit.services import record_event
from core.exceptions import DomainError

ALLOWED_TRANSITIONS = {
    ApprovalStatus.DRAFT: {ApprovalStatus.IN_REVIEW, ApprovalStatus.SUPERSEDED},
    ApprovalStatus.IN_REVIEW: {
        ApprovalStatus.APPROVED,
        ApprovalStatus.REJECTED,
        ApprovalStatus.SUPERSEDED,
    },
    ApprovalStatus.REJECTED: {ApprovalStatus.DRAFT, ApprovalStatus.SUPERSEDED},
    ApprovalStatus.APPROVED: {ApprovalStatus.SUPERSEDED},
    ApprovalStatus.SUPERSEDED: set(),
}


def get_or_create_approval(*, project, target):
    approval, _ = Approval.objects.get_or_create(
        project=project,
        target=target,
        status__in=[ApprovalStatus.DRAFT, ApprovalStatus.IN_REVIEW, ApprovalStatus.APPROVED],
        defaults={"status": ApprovalStatus.DRAFT},
    )
    return approval


@transaction.atomic
def transition_approval(*, approval, new_status, actor=None, reason=""):
    allowed = ALLOWED_TRANSITIONS.get(ApprovalStatus(approval.status), set())
    if new_status not in allowed:
        raise DomainError(
            f"'{approval.status}' 상태에서 '{new_status}'로 전이할 수 없습니다.",
            code="invalid_approval_transition",
            status_code=409,
            details={"from": approval.status, "to": new_status, "allowed": sorted(allowed)},
        )

    # Vendor 생성/릴리스 승인은 CRITICAL 검증을 통과해야 한다 (§22)
    if new_status == ApprovalStatus.APPROVED and approval.target in GENERATION_TARGETS:
        from apps.validation.services import assert_generation_allowed

        assert_generation_allowed(approval.project)

    before = approval.status
    approval.status = new_status
    if new_status in (ApprovalStatus.APPROVED, ApprovalStatus.REJECTED):
        approval.approver = actor if actor and actor.is_authenticated else None
    approval.reason = reason
    approval.save(update_fields=["status", "approver", "reason", "updated_at"])

    ApprovalHistory.objects.create(
        approval=approval,
        from_status=before,
        to_status=new_status,
        actor=actor if actor and actor.is_authenticated else None,
        reason=reason,
    )
    record_event(
        actor=actor,
        action=f"APPROVAL_{new_status}",
        object_type="Approval",
        object_id=approval.id,
        before={"status": before},
        after={"status": new_status, "target": approval.target},
        reason=reason,
    )
    return approval


def submit_for_review(*, project, target, actor=None):
    approval = get_or_create_approval(project=project, target=target)
    if approval.status == ApprovalStatus.DRAFT:
        return transition_approval(
            approval=approval, new_status=ApprovalStatus.IN_REVIEW, actor=actor
        )
    return approval
