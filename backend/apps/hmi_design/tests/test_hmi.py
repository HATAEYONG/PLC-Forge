"""HMI Design 테스트 (PRD §17): 조건부 화면 생성."""

import pytest

from apps.hmi_design.services import generate_hmi
from apps.io_points.services import estimate_io
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
def test_no_hmi_when_not_required(project):
    result = generate_hmi(project=project)
    assert result["screens"] == 0
    assert project.hmi_screens.count() == 0


@pytest.mark.django_db
def test_base_screens_created(project):
    set_fact(project, "HMI_REQUIRED", True, ValueType.BOOLEAN)
    generate_hmi(project=project)
    codes = set(project.hmi_screens.values_list("code", flat=True))
    assert {"MAIN_OVERVIEW", "ALARM_SUMMARY"} <= codes


@pytest.mark.django_db
def test_recipe_screen_conditional(project):
    set_fact(project, "HMI_REQUIRED", True, ValueType.BOOLEAN)
    generate_hmi(project=project)
    assert not project.hmi_screens.filter(code="RECIPE").exists()

    set_fact(project, "RECIPE_REQUIRED", True, ValueType.BOOLEAN)
    generate_hmi(project=project)
    assert project.hmi_screens.filter(code="RECIPE").exists()


@pytest.mark.django_db
def test_trend_and_auto_sequence_conditional(project):
    set_fact(project, "HMI_REQUIRED", True, ValueType.BOOLEAN)
    set_fact(project, "TREND_REQUIRED", True, ValueType.BOOLEAN)
    set_fact(project, "CONTROL_MODE", "AUTO", ValueType.STRING)
    generate_hmi(project=project)
    codes = set(project.hmi_screens.values_list("code", flat=True))
    assert {"TREND", "AUTO_SEQUENCE"} <= codes


@pytest.mark.django_db
def test_io_monitor_derives_tags(project):
    set_fact(project, "HMI_REQUIRED", True, ValueType.BOOLEAN)
    set_fact(project, "DEVICE_LIST", ["모터"], ValueType.LIST)
    estimate_io(project=project)
    generate_hmi(project=project)
    io_screen = project.hmi_screens.get(code="IO_MONITOR")
    assert io_screen.tags.count() == 3  # 모터 DO+2DI
    assert io_screen.security_level == "ENGINEER"


@pytest.mark.django_db
def test_hmi_idempotent(project):
    set_fact(project, "HMI_REQUIRED", True, ValueType.BOOLEAN)
    generate_hmi(project=project)
    count = project.hmi_screens.count()
    generate_hmi(project=project)
    assert project.hmi_screens.count() == count
