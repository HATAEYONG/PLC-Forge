"""Validation Engine 테스트 (PRD §22)."""

import pytest

from apps.alarms.services import generate_alarms
from apps.design.models import RiskLevel
from apps.design.services import create_design_decision
from apps.interlocks.models import Interlock
from apps.io_points.models import IOPoint
from apps.projects.tests.factories import ProjectFactory
from apps.requirements.models import SourceType, ValueType
from apps.requirements.services import create_fact
from apps.sensors.models import SensorRequirement
from apps.validation.engine import (
    check_duplicate_tag,
    check_interlock_coverage,
    check_missing_sensor,
    check_unsafe_bypass,
    run_validation,
)
from apps.validation.models import Severity


@pytest.fixture
def project(db):
    return ProjectFactory()


def set_fact(project, key, value, vtype):
    return create_fact(
        project=project,
        fact_key=key,
        value_json=value,
        value_type=vtype,
        source_type=SourceType.MANUAL,
    )


@pytest.mark.django_db
def test_duplicate_tag_check_no_false_positive(project):
    # DB 유니크 제약이 중복을 1차 방어하므로 정상(유일 태그)에서는 Finding이 없어야 한다.
    IOPoint.objects.create(project=project, tag="T1", signal_type="DI")
    IOPoint.objects.create(project=project, tag="T2", signal_type="DO")
    assert check_duplicate_tag(project, {}) == []


def test_duplicate_tag_check_flags_critical(monkeypatch):
    # 방어적 계층: 중복 태그가 실제로 존재하면 CRITICAL을 반환한다.
    from apps.validation import engine

    class _FakeIO:
        @staticmethod
        def values_list(field, flat=False):
            return ["DUP", "DUP", "OK"]

    fake_project = type("P", (), {"io_points": _FakeIO()})()
    findings = engine.check_duplicate_tag(fake_project, {})
    assert findings and findings[0]["severity"] == Severity.CRITICAL


@pytest.mark.django_db
def test_missing_sensor_detected(project):
    findings = check_missing_sensor(project, {"MEASUREMENT_REQUIREMENTS": ["LEVEL"]})
    assert any(f["code"] == "MISSING_SENSOR" for f in findings)
    SensorRequirement.objects.create(project=project, measurement_type="LEVEL")
    findings2 = check_missing_sensor(project, {"MEASUREMENT_REQUIREMENTS": ["LEVEL"]})
    assert not findings2


@pytest.mark.django_db
def test_interlock_coverage_gap_is_critical(project):
    fact = set_fact(project, "ESTOP_REQUIRED", True, ValueType.BOOLEAN)
    create_design_decision(
        project=project,
        decision_type="INTERLOCK_REQUIREMENT",
        subject_type="INTERLOCK",
        subject_id="ESTOP",
        decision_value={},
        reason="비상정지",
        input_facts=[fact],
        risk_level=RiskLevel.CRITICAL,
    )
    findings = check_interlock_coverage(project, {})
    assert findings[0]["severity"] == Severity.CRITICAL


@pytest.mark.django_db
def test_unsafe_bypass_detected(project):
    Interlock.objects.create(
        project=project,
        code="IL_X",
        safety_related=True,
        bypass_allowed=True,
        bypass_permission="",
    )
    findings = check_unsafe_bypass(project, {})
    assert findings[0]["code"] == "UNSAFE_BYPASS"
    assert findings[0]["severity"] == Severity.CRITICAL


@pytest.mark.django_db
def test_run_validation_persists_and_summarizes(project):
    set_fact(project, "STEAM_PRESENT", True, ValueType.BOOLEAN)
    create_design_decision(
        project=project,
        decision_type="ALARM_REQUIREMENT",
        subject_type="ALARM",
        subject_id="X",
        decision_value={"type": "HIGH"},
        reason="테스트",
        input_facts=[project.facts.first()],
    )
    generate_alarms(project=project)
    summary = run_validation(project)
    assert summary["total"] == project.validation_findings.count()
    assert "CRITICAL" in summary["by_severity"]
