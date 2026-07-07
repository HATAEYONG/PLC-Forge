"""I/O Estimation 테스트 (PRD §13)."""

import pytest

from apps.io_points.services import estimate_io
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
def test_device_io_profiles_generate_points(project):
    set_fact(project, "DEVICE_LIST", ["펌프", "밸브"], ValueType.LIST)
    result = estimate_io(project=project)
    # 펌프(DO+2DI) + 밸브(DO+2DI) = DO 2, DI 4
    assert result["counts"]["DO"] == 2
    assert result["counts"]["DI"] == 4
    assert result["total"] == 6


@pytest.mark.django_db
def test_sensor_io_included(project):
    set_fact(project, "DEVICE_LIST", ["모터"], ValueType.LIST)
    set_fact(project, "MEASUREMENT_REQUIREMENTS", ["TEMPERATURE"], ValueType.LIST)
    generate_sensor_requirements(project=project)
    result = estimate_io(project=project)
    # 온도 센서 → AI 1점
    assert result["counts"]["AI"] == 1
    assert project.io_points.filter(source_type="SENSOR").count() == 1


@pytest.mark.django_db
def test_tags_are_unique(project):
    set_fact(project, "DEVICE_LIST", ["펌프", "펌프"], ValueType.LIST)
    estimate_io(project=project)
    tags = list(project.io_points.values_list("tag", flat=True))
    assert len(tags) == len(set(tags))


@pytest.mark.django_db
def test_io_is_idempotent(project):
    set_fact(project, "DEVICE_LIST", ["모터"], ValueType.LIST)
    estimate_io(project=project)
    estimate_io(project=project)
    assert project.io_points.filter(source_type="DEVICE").count() == 3
