"""FAT/SAT 테스트 생성 + 커버리지 (PRD §24)."""

import pytest

from apps.alarms.services import generate_alarms
from apps.design.models import RiskLevel
from apps.design.services import create_design_decision
from apps.fat_sat.models import TestPhase
from apps.fat_sat.services import generate_tests
from apps.interlocks.services import generate_interlocks
from apps.projects.tests.factories import ProjectFactory
from apps.requirements.models import SourceType, ValueType
from apps.requirements.services import create_fact
from apps.sensors.services import generate_sensor_requirements
from apps.sequences.services import generate_sequence


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


def build_full_design(project):
    set_fact(project, "MEASUREMENT_REQUIREMENTS", ["TEMPERATURE"], ValueType.LIST)
    set_fact(project, "CONTROL_MODE", "AUTO", ValueType.STRING)
    generate_sensor_requirements(project=project)
    fact = set_fact(project, "ESTOP_REQUIRED", True, ValueType.BOOLEAN)
    create_design_decision(
        project=project,
        decision_type="INTERLOCK_REQUIREMENT",
        subject_type="INTERLOCK",
        subject_id="ESTOP_TRIP",
        decision_value={"effect": "STOP"},
        reason="비상정지",
        input_facts=[fact],
        risk_level=RiskLevel.CRITICAL,
    )
    create_design_decision(
        project=project,
        decision_type="ALARM_REQUIREMENT",
        subject_type="ALARM",
        subject_id="TEMP_HIGH",
        decision_value={"type": "HIGH_TEMP", "priority": "HIGH"},
        reason="과열 알람",
        input_facts=[fact],
    )
    generate_interlocks(project=project)
    generate_alarms(project=project)
    generate_sequence(project=project)


@pytest.mark.django_db
def test_tests_generated_for_all_artifacts(project):
    build_full_design(project)
    result = generate_tests(project=project)
    assert result["fat"] > 0 and result["sat"] > 0

    categories = set(project.test_cases.values_list("category", flat=True))
    assert {"SENSOR", "ALARM", "INTERLOCK", "SEQUENCE"} <= categories


@pytest.mark.django_db
def test_every_alarm_and_interlock_covered(project):
    build_full_design(project)
    generate_tests(project=project)

    # 각 알람이 FAT 테스트로 커버됨 (source_ref 역추적)
    for alarm in project.alarms.all():
        assert project.test_cases.filter(
            phase=TestPhase.FAT, source_type="ALARM", source_ref=alarm.code
        ).exists()
    for interlock in project.interlocks.all():
        assert project.test_cases.filter(
            source_type="INTERLOCK", source_ref=interlock.code
        ).exists()


@pytest.mark.django_db
def test_result_can_be_recorded_via_api(api_client, project):
    build_full_design(project)
    generate_tests(project=project)
    test = project.test_cases.first()
    response = api_client.patch(
        f"/api/test-cases/{test.id}/",
        {"status": "PASS", "actual_result": "정상", "tester": "홍길동"},
        format="json",
    )
    assert response.status_code == 200
    test.refresh_from_db()
    assert test.status == "PASS"
    assert test.tester == "홍길동"
