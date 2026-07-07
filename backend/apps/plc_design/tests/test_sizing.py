"""PLC Sizing 테스트 (PRD §15)."""

import pytest

from apps.io_points.services import estimate_io
from apps.plc_design.models import PLCClass
from apps.plc_design.services import size_plc
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
def test_small_io_selects_micro_class(project):
    set_fact(project, "DEVICE_LIST", ["모터"], ValueType.LIST)
    estimate_io(project=project)
    sizing = size_plc(project=project)
    assert sizing.required_class == PLCClass.MICRO
    assert sizing.minimum_spec_json["min_do"] >= 1


@pytest.mark.django_db
def test_redundancy_forces_high_end(project):
    set_fact(project, "DEVICE_LIST", ["모터"], ValueType.LIST)
    set_fact(project, "REDUNDANCY_REQUIRED", True, ValueType.BOOLEAN)
    estimate_io(project=project)
    sizing = size_plc(project=project)
    assert sizing.required_class == PLCClass.HIGH_END


@pytest.mark.django_db
def test_safety_io_selects_modular(project):
    set_fact(project, "DEVICE_LIST", ["모터"], ValueType.LIST)
    set_fact(project, "ESTOP_REQUIRED", True, ValueType.BOOLEAN)
    estimate_io(project=project)
    sizing = size_plc(project=project)
    assert sizing.required_class == PLCClass.MODULAR
    assert sizing.factors_json["safety_io"] is True


@pytest.mark.django_db
def test_existing_vendor_prioritized_and_others_rejected(project):
    set_fact(project, "DEVICE_LIST", ["모터"], ValueType.LIST)
    set_fact(project, "EXISTING_PLC_VENDOR", "LS", ValueType.STRING)
    estimate_io(project=project)
    sizing = size_plc(project=project)
    accepted = sizing.candidates.filter(accepted=True)
    rejected = sizing.candidates.filter(accepted=False)
    # 기존 벤더(LS)만 채택, 나머지는 사유와 함께 탈락 (§15 Rejected Candidates and Reasons)
    assert accepted.count() == 1
    assert accepted.first().vendor == "LS ELECTRIC"
    assert rejected.exists()
    assert all(c.reason for c in rejected)


@pytest.mark.django_db
def test_future_expansion_increases_margin(project):
    set_fact(project, "DEVICE_LIST", ["모터"], ValueType.LIST)
    set_fact(project, "FUTURE_EXPANSION", True, ValueType.BOOLEAN)
    estimate_io(project=project)
    sizing = size_plc(project=project)
    assert sizing.spare_margin_percent == 30
