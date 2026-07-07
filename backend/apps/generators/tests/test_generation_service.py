"""Vendor 생성 서비스 + CRITICAL 차단 테스트 (PRD §21, §22)."""

import pytest

from apps.generators.services import generate_vendor_package
from apps.io_points.models import IOPoint
from apps.projects.tests.factories import ProjectFactory
from apps.validation.models import Severity, ValidationFinding
from core.exceptions import DomainError


@pytest.fixture
def project(db):
    p = ProjectFactory(code="GEN-1")
    IOPoint.objects.create(project=p, tag="PUMP_RUN", signal_type="DO", description="기동")
    IOPoint.objects.create(project=p, tag="LEVEL_AI", signal_type="AI", description="레벨")
    return p


@pytest.mark.django_db
def test_generation_blocked_by_critical(project):
    ValidationFinding.objects.create(
        project=project, severity=Severity.CRITICAL, code="DUP", title="중복", status="OPEN"
    )
    with pytest.raises(DomainError) as excinfo:
        generate_vendor_package(project=project, vendor="ls")
    assert excinfo.value.code == "critical_findings_block_generation"


@pytest.mark.django_db
def test_unknown_vendor_rejected(project):
    with pytest.raises(DomainError) as excinfo:
        generate_vendor_package(project=project, vendor="foobar")
    assert excinfo.value.code == "unknown_vendor"


@pytest.mark.django_db
def test_generation_end_to_end(project):
    result = generate_vendor_package(project=project, vendor="ls")
    assert result["vendor"] == "LS ELECTRIC"
    assert "Main.st" in result["files"]
    assert result["mapping_report"]["signal_count"] == 2
    # 감사 기록
    from apps.audit.models import AuditEvent

    assert AuditEvent.objects.filter(action="VENDOR_CODE_GENERATED").exists()


@pytest.mark.django_db
def test_generation_api(api_client, project):
    response = api_client.post(f"/api/projects/{project.id}/vendor-generate/?vendor=ls")
    assert response.status_code == 201
    body = response.json()
    assert body["vendor"] == "LS ELECTRIC"
    assert "Main.st" in body["files"]
    assert "PROGRAM Main" in body["files"]["Main.st"]
