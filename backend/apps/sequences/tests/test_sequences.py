"""Sequence 생성 테스트 (PRD §19)."""

import pytest

from apps.projects.tests.factories import ProjectFactory
from apps.requirements.models import SourceType, ValueType
from apps.requirements.services import create_fact
from apps.sequences.services import generate_sequence


@pytest.fixture
def project(db):
    return ProjectFactory()


def set_mode(project, mode):
    return create_fact(
        project=project,
        fact_key="CONTROL_MODE",
        value_json=mode,
        value_type=ValueType.STRING,
        source_type=SourceType.MANUAL,
    )


@pytest.mark.django_db
def test_no_sequence_for_manual_mode(project):
    set_mode(project, "MANUAL")
    result = generate_sequence(project=project)
    assert result["sequences"] == 0


@pytest.mark.django_db
def test_auto_mode_generates_sequence_steps(project):
    set_mode(project, "AUTO")
    result = generate_sequence(project=project)
    assert result["sequences"] == 1
    sequence = project.sequences.get(code="SEQ_MAIN")
    assert sequence.steps.count() == 3
    # 스텝에 타임아웃/알람/abort 조건이 채워짐 (§19)
    ready = sequence.steps.get(step_no=1)
    assert ready.timeout_seconds == 30
    assert ready.timeout_alarm
    assert ready.abort_condition
    assert sequence.decision is not None


@pytest.mark.django_db
def test_sequence_idempotent(project):
    set_mode(project, "AUTO")
    generate_sequence(project=project)
    generate_sequence(project=project)
    assert project.sequences.count() == 1
