"""Communication Design 테스트 (PRD §16)."""

import pytest

from apps.communications.models import FailureBehavior
from apps.communications.services import generate_communication
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


@pytest.mark.django_db
def test_hmi_and_inverter_links(project):
    set_fact(project, "HMI_REQUIRED", True, ValueType.BOOLEAN)
    set_fact(project, "INVERTER_USED", True, ValueType.BOOLEAN)
    result = generate_communication(project=project)
    assert result["nodes"] >= 3  # PLC + HMI + INVERTER
    # 인버터 링크는 통신 두절 시 안전 상태
    inv_link = project.comm_links.filter(target__node_type="INVERTER").first()
    assert inv_link.failure_behavior == FailureBehavior.SAFE_STATE
    assert project.comm_links.filter(target__node_type="HMI").exists()


@pytest.mark.django_db
def test_scada_requires_opc_ua(project):
    set_fact(project, "SCADA_REQUIRED", True, ValueType.BOOLEAN)
    generate_communication(project=project)
    assert project.protocol_requirements.filter(requirement="OPC_UA").exists()
    assert project.comm_links.filter(protocol="OPC UA").exists()


@pytest.mark.django_db
def test_mes_integration_adds_gateway(project):
    set_fact(project, "MES_INTEGRATION_REQUIRED", True, ValueType.BOOLEAN)
    generate_communication(project=project)
    reqs = set(project.protocol_requirements.values_list("requirement", flat=True))
    assert {"MQTT", "GATEWAY"} <= reqs
    assert project.comm_nodes.filter(node_type="GATEWAY").exists()


@pytest.mark.django_db
def test_traceability_and_idempotent(project):
    set_fact(project, "HMI_REQUIRED", True, ValueType.BOOLEAN)
    generate_communication(project=project)
    generate_communication(project=project)
    link = project.comm_links.first()
    assert link.decision is not None
    assert link.decision.input_facts.exists()
    # 재실행해도 중복 누적 없음
    assert project.comm_nodes.filter(node_type="HMI").count() == 1
