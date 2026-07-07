"""Design Engine 오케스트레이션 end-to-end 테스트 (Phase 4-A: sensor→io→plc)."""

import pytest

from apps.projects.tests.factories import ProjectFactory
from apps.requirements.models import SourceType, ValueType
from apps.requirements.services import create_fact


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


def seed_food_tank_project(project):
    from django.core.management import call_command

    call_command("load_knowledge")
    set_fact(project, "DEVICE_LIST", ["펌프", "히터", "밸브"], ValueType.LIST)
    set_fact(project, "MEASUREMENT_REQUIREMENTS", ["LEVEL", "TEMPERATURE"], ValueType.LIST)
    set_fact(project, "CONTINUOUS_LEVEL_REQUIRED", True, ValueType.BOOLEAN)
    set_fact(project, "STEAM_PRESENT_DURING_CIP", True, ValueType.BOOLEAN)
    set_fact(project, "CIP_REQUIRED", True, ValueType.BOOLEAN)
    set_fact(project, "EXISTING_PLC_VENDOR", "LS", ValueType.STRING)
    set_fact(project, "HMI_REQUIRED", True, ValueType.BOOLEAN)
    set_fact(project, "INVERTER_USED", True, ValueType.BOOLEAN)
    set_fact(project, "CONTROL_MODE", "AUTO", ValueType.STRING)


@pytest.mark.django_db
def test_generate_design_all_stages_api(api_client, project):
    seed_food_tank_project(project)
    response = api_client.post(f"/api/projects/{project.id}/generate-design/?stage=all")
    assert response.status_code == 201
    summary = response.json()["summary"]
    assert summary["sensor"]["count"] == 2
    assert summary["io"]["total"] > 0
    assert summary["plc"]["required_class"]
    assert summary["comm"]["nodes"] >= 2
    assert summary["hmi"]["screens"] > 0
    assert summary["sequence"]["sequences"] == 1
    assert summary["test"]["total"] > 0

    # 산출물 조회 + Traceability 체인 (I/O → sensor requirement → decision → fact)
    sensors = api_client.get(f"/api/sensor-requirements/?project={project.id}").json()
    assert sensors["count"] == 2
    io = api_client.get(f"/api/io-points/?project={project.id}").json()
    assert io["count"] > 0
    plc = api_client.get(f"/api/plc-sizing/?project={project.id}").json()
    assert plc["count"] == 1
    assert plc["results"][0]["candidates"]


@pytest.mark.django_db
def test_full_traceability_chain(project):
    from apps.design.orchestrator import generate_design

    seed_food_tank_project(project)
    generate_design(project=project, stage="all")

    # I/O(센서 유래) → SensorRequirement → DesignDecision → 입력 Fact 로 역추적
    sensor_io = project.io_points.filter(source_type="SENSOR").first()
    assert sensor_io is not None
    requirement = sensor_io.sensor_requirement
    assert requirement is not None
    decision = requirement.decision
    assert decision is not None
    assert decision.input_facts.exists()


@pytest.mark.django_db
def test_unknown_stage_rejected(api_client, project):
    response = api_client.post(f"/api/projects/{project.id}/generate-design/?stage=nonsense")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "unknown_stage"
