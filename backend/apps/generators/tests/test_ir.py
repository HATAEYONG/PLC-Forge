"""Vendor Independent IR 테스트 (PRD §20)."""

import pytest

from apps.alarms.services import generate_alarms
from apps.design.models import RiskLevel
from apps.design.services import create_design_decision
from apps.generators.ir import OPERATIONS, build_ir, validate_ir
from apps.interlocks.services import generate_interlocks
from apps.io_points.services import estimate_io
from apps.projects.tests.factories import ProjectFactory
from apps.requirements.models import SourceType, ValueType
from apps.requirements.services import create_fact
from core.exceptions import DomainError


@pytest.fixture
def project(db):
    p = ProjectFactory(code="IR-1")
    fact = create_fact(
        project=p,
        fact_key="DEVICE_LIST",
        value_json=["펌프"],
        value_type=ValueType.LIST,
        source_type=SourceType.MANUAL,
    )
    estimate_io(project=p)
    create_design_decision(
        project=p,
        decision_type="INTERLOCK_REQUIREMENT",
        subject_type="INTERLOCK",
        subject_id="ESTOP",
        decision_value={"effect": "STOP"},
        reason="비상정지",
        input_facts=[fact],
        risk_level=RiskLevel.CRITICAL,
    )
    create_design_decision(
        project=p,
        decision_type="ALARM_REQUIREMENT",
        subject_type="ALARM",
        subject_id="TEMP_HIGH",
        decision_value={"type": "HIGH", "priority": "HIGH"},
        reason="과열",
        input_facts=[fact],
    )
    generate_interlocks(project=p)
    generate_alarms(project=p)
    return p


@pytest.mark.django_db
def test_build_ir_has_required_sections(project):
    ir = build_ir(project)
    for key in [
        "project_metadata",
        "signal_definitions",
        "data_types",
        "logic_expressions",
        "alarms",
        "interlocks",
        "sequences",
        "hmi_tags",
        "test_requirements",
    ]:
        assert key in ir
    assert ir["project_metadata"]["code"] == "IR-1"
    assert len(ir["signal_definitions"]) == project.io_points.count()


@pytest.mark.django_db
def test_ir_validates_against_schema(project):
    validate_ir(build_ir(project))  # 예외 없음


@pytest.mark.django_db
def test_logic_expressions_use_known_operations(project):
    ir = build_ir(project)
    assert ir["logic_expressions"]
    for expr in ir["logic_expressions"]:
        assert expr["operation"] in OPERATIONS


@pytest.mark.django_db
def test_invalid_ir_rejected(project):
    ir = build_ir(project)
    ir["signal_definitions"][0]["signal_type"] = "XX"  # 스키마 위반
    with pytest.raises(DomainError) as excinfo:
        validate_ir(ir)
    assert excinfo.value.code == "invalid_ir"
