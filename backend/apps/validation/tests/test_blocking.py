"""CRITICAL Finding 차단 게이트 테스트 (PRD §22, §33-14)."""

import pytest

from apps.approvals.models import ApprovalStatus, ApprovalTarget
from apps.approvals.services import submit_for_review, transition_approval
from apps.io_points.models import IOPoint
from apps.projects.tests.factories import ProjectFactory
from apps.validation.models import Severity, ValidationFinding
from apps.validation.services import assert_generation_allowed
from core.exceptions import DomainError


@pytest.fixture
def project(db):
    return ProjectFactory()


def add_critical(project):
    ValidationFinding.objects.create(
        project=project,
        severity=Severity.CRITICAL,
        code="DUPLICATE_TAG",
        title="중복 태그",
        status="OPEN",
    )


@pytest.mark.django_db
def test_assert_generation_blocked_by_critical(project):
    add_critical(project)
    with pytest.raises(DomainError) as excinfo:
        assert_generation_allowed(project)
    assert excinfo.value.code == "critical_findings_block_generation"


@pytest.mark.django_db
def test_assert_generation_allowed_when_clean(project):
    # 산출물 없음 → 검증 실행돼도 CRITICAL 없음
    assert_generation_allowed(project)  # 예외 없음


@pytest.mark.django_db
def test_vendor_code_approval_blocked_by_critical(project, user):
    add_critical(project)
    submit_for_review(project=project, target=ApprovalTarget.VENDOR_CODE_GENERATION, actor=user)
    approval = project.approvals.get(target=ApprovalTarget.VENDOR_CODE_GENERATION)
    with pytest.raises(DomainError) as excinfo:
        transition_approval(
            approval=approval, new_status=ApprovalStatus.APPROVED, actor=user, reason="승인 시도"
        )
    assert excinfo.value.code == "critical_findings_block_generation"


@pytest.mark.django_db
def test_resolved_critical_unblocks(project, user):
    finding = ValidationFinding.objects.create(
        project=project, severity=Severity.CRITICAL, code="X", title="t", status="OPEN"
    )
    IOPoint.objects.create(project=project, tag="A", signal_type="DI")
    finding.status = "WAIVED"
    finding.save()
    # WAIVED는 차단 대상이 아님 → 통과
    assert_generation_allowed(project)
