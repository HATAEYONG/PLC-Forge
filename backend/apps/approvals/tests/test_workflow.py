"""Approval Workflow 테스트 (PRD §23)."""

import pytest

from apps.approvals.models import Approval, ApprovalStatus, ApprovalTarget
from apps.approvals.services import get_or_create_approval, submit_for_review, transition_approval
from apps.audit.models import AuditEvent
from apps.projects.tests.factories import ProjectFactory
from core.exceptions import DomainError


@pytest.fixture
def project(db):
    return ProjectFactory()


@pytest.mark.django_db
def test_full_approval_flow(project, user):
    approval = submit_for_review(project=project, target=ApprovalTarget.SENSOR_DESIGN, actor=user)
    assert approval.status == ApprovalStatus.IN_REVIEW
    approval = transition_approval(
        approval=approval, new_status=ApprovalStatus.APPROVED, actor=user, reason="검토 완료"
    )
    assert approval.status == ApprovalStatus.APPROVED
    assert approval.approver == user
    # 상태 이력 + 감사 기록
    assert approval.history.count() == 2
    assert AuditEvent.objects.filter(action="APPROVAL_APPROVED").exists()


@pytest.mark.django_db
def test_skip_transition_rejected(project, user):
    approval = get_or_create_approval(project=project, target=ApprovalTarget.PLC_DESIGN)
    # DRAFT → APPROVED 건너뛰기 금지
    with pytest.raises(DomainError) as excinfo:
        transition_approval(approval=approval, new_status=ApprovalStatus.APPROVED, actor=user)
    assert excinfo.value.code == "invalid_approval_transition"


@pytest.mark.django_db
def test_rejected_can_return_to_draft(project, user):
    approval = submit_for_review(project=project, target=ApprovalTarget.HMI_DESIGN, actor=user)
    transition_approval(
        approval=approval, new_status=ApprovalStatus.REJECTED, actor=user, reason="수정 필요"
    )
    approval = transition_approval(approval=approval, new_status=ApprovalStatus.DRAFT, actor=user)
    assert approval.status == ApprovalStatus.DRAFT


@pytest.mark.django_db
def test_approval_api_flow(api_client, project):
    submit = api_client.post(
        f"/api/projects/{project.id}/submit-review/",
        {"target": "SENSOR_DESIGN"},
        format="json",
    )
    assert submit.status_code == 201
    approval_id = submit.json()["id"]

    approve = api_client.post(
        f"/api/approvals/{approval_id}/approve/", {"reason": "OK"}, format="json"
    )
    assert approve.status_code == 200
    assert approve.json()["status"] == "APPROVED"

    listed = api_client.get(f"/api/approvals/?project={project.id}")
    assert listed.json()["count"] == 1


@pytest.mark.django_db
def test_active_target_uniqueness(project, user):
    submit_for_review(project=project, target=ApprovalTarget.FAT_PLAN, actor=user)
    # 같은 대상 재제출은 기존 활성 승인을 반환(중복 생성 안 함)
    submit_for_review(project=project, target=ApprovalTarget.FAT_PLAN, actor=user)
    assert Approval.objects.filter(project=project, target=ApprovalTarget.FAT_PLAN).count() == 1
