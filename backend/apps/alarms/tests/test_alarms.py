"""Alarm 생성 테스트 (PRD §18)."""

import pytest

from apps.alarms.services import generate_alarms
from apps.design.services import create_design_decision
from apps.projects.tests.factories import ProjectFactory
from apps.requirements.models import SourceType, ValueType
from apps.requirements.services import create_fact


@pytest.fixture
def project(db):
    return ProjectFactory()


@pytest.mark.django_db
def test_alarm_materialized_from_decision(project):
    fact = create_fact(
        project=project,
        fact_key="STEAM_PRESENT",
        value_json=True,
        value_type=ValueType.BOOLEAN,
        source_type=SourceType.MANUAL,
    )
    create_design_decision(
        project=project,
        decision_type="ALARM_REQUIREMENT",
        subject_type="ALARM",
        subject_id="LEVEL_HIGH",
        decision_value={"type": "HIGH_LEVEL", "priority": "HIGH"},
        reason="증기 환경 고수위 보호",
        input_facts=[fact],
    )
    result = generate_alarms(project=project)
    assert result["alarms"] == 1
    alarm = project.alarms.get(code="AL_LEVEL_HIGH")
    assert alarm.priority == "HIGH"
    assert alarm.latching is True
    assert alarm.decision is not None  # Traceability


@pytest.mark.django_db
def test_communication_alarm_generated(project):
    from apps.communications.services import generate_communication

    create_fact(
        project=project,
        fact_key="SCADA_REQUIRED",
        value_json=True,
        value_type=ValueType.BOOLEAN,
        source_type=SourceType.MANUAL,
    )
    generate_communication(project=project)
    generate_alarms(project=project)
    assert project.alarms.filter(source="COMMUNICATION").exists()
