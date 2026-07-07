"""Sensor Design 테스트 (PRD §14)."""

import pytest

from apps.projects.tests.factories import ProjectFactory
from apps.requirements.models import SourceType, ValueType
from apps.requirements.services import create_fact
from apps.sensors.services import generate_sensor_requirements


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
def test_steam_continuous_level_selects_radar(project):
    from django.core.management import call_command

    call_command("load_knowledge")
    set_fact(project, "MEASUREMENT_REQUIREMENTS", ["LEVEL"], ValueType.LIST)
    set_fact(project, "CONTINUOUS_LEVEL_REQUIRED", True, ValueType.BOOLEAN)
    set_fact(project, "STEAM_PRESENT_DURING_CIP", True, ValueType.BOOLEAN)

    requirements = generate_sensor_requirements(project=project)
    level = next(r for r in requirements if r.measurement_type == "LEVEL")
    assert level.measurement_principle == "RADAR"
    assert level.signal_type == "AI"
    assert "HART" in level.communication_requirements
    # Traceability: decision과 근거 Fact/지식 연결
    assert level.decision is not None
    assert level.decision.input_facts.exists()
    assert level.decision.knowledge_items.filter(code="KB-SEN-LEVEL-RADAR").exists()


@pytest.mark.django_db
def test_level_switch_when_not_continuous(project):
    set_fact(project, "MEASUREMENT_REQUIREMENTS", ["LEVEL"], ValueType.LIST)
    set_fact(project, "CONTINUOUS_LEVEL_REQUIRED", False, ValueType.BOOLEAN)
    requirements = generate_sensor_requirements(project=project)
    level = requirements[0]
    assert level.signal_type == "DI"
    assert level.measurement_principle == "FLOAT_SWITCH"


@pytest.mark.django_db
def test_sanitary_and_cip_environment_applied(project):
    set_fact(project, "MEASUREMENT_REQUIREMENTS", ["TEMPERATURE"], ValueType.LIST)
    set_fact(project, "SANITARY_REQUIRED", True, ValueType.BOOLEAN)
    set_fact(project, "CIP_REQUIRED", True, ValueType.BOOLEAN)
    req = generate_sensor_requirements(project=project)[0]
    assert req.measurement_principle == "RTD"
    assert "위생" in req.material_compatibility
    assert "IP69K" in req.environmental_rating


@pytest.mark.django_db
def test_generate_is_idempotent(project):
    set_fact(project, "MEASUREMENT_REQUIREMENTS", ["TEMPERATURE", "PRESSURE"], ValueType.LIST)
    generate_sensor_requirements(project=project)
    generate_sensor_requirements(project=project)
    assert project.sensor_requirements.count() == 2
