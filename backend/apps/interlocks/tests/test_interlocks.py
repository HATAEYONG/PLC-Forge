"""Interlock + Cause & Effect 테스트 (PRD §18)."""

import pytest

from apps.alarms.services import generate_alarms
from apps.design.models import RiskLevel
from apps.design.services import create_design_decision
from apps.interlocks.services import cause_effect_matrix, generate_interlocks
from apps.projects.tests.factories import ProjectFactory
from apps.requirements.models import SourceType, ValueType
from apps.requirements.services import create_fact


@pytest.fixture
def project(db):
    return ProjectFactory()


def estop_decision(project):
    fact = create_fact(
        project=project,
        fact_key="ESTOP_REQUIRED",
        value_json=True,
        value_type=ValueType.BOOLEAN,
        source_type=SourceType.MANUAL,
    )
    return create_design_decision(
        project=project,
        decision_type="INTERLOCK_REQUIREMENT",
        subject_type="INTERLOCK",
        subject_id="ESTOP_TRIP",
        decision_value={"effect": "STOP_ALL_ACTUATORS", "reset": "MANUAL"},
        reason="비상정지 보호",
        input_facts=[fact],
        risk_level=RiskLevel.CRITICAL,
    )


@pytest.mark.django_db
def test_safety_interlock_requires_bypass_permission(project):
    estop_decision(project)
    generate_interlocks(project=project)
    interlock = project.interlocks.get(code="IL_ESTOP_TRIP")
    assert interlock.safety_related is True
    # Safety 인터록은 임의 바이패스 불가, 권한 정책 명시 (PRD §3.5)
    assert interlock.bypass_allowed is False
    assert interlock.bypass_permission
    assert interlock.decision is not None


@pytest.mark.django_db
def test_cause_effect_matrix_built(project):
    estop_decision(project)
    generate_interlocks(project=project)
    create_design_decision(
        project=project,
        decision_type="ALARM_REQUIREMENT",
        subject_type="INTERLOCK",
        subject_id="ESTOP_TRIP",
        decision_value={"type": "ESTOP", "priority": "CRITICAL"},
        reason="비상정지 알람",
        input_facts=[project.facts.first()],
    )
    generate_alarms(project=project)

    matrix = cause_effect_matrix(project=project)
    assert matrix["causes"]
    assert matrix["effects"] == ["IL_ESTOP_TRIP"]
    # 최소 하나의 원인이 인터록 효과와 연관됨
    assert any(any(row["effects"].values()) for row in matrix["matrix"])
