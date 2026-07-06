"""인터뷰 종료조건 테스트 (PRD §8.6)."""

import pytest

from apps.interview.completion import REQUIRED_FACT_CRITERIA, evaluate_completion
from apps.interview.services import complete_session
from apps.interview.tests.factories import InterviewSessionFactory, QuestionFactory
from apps.requirements.models import SourceType, ValueType
from apps.requirements.services import create_fact
from core.exceptions import DomainError

ALL_REQUIRED_KEYS = set().union(*REQUIRED_FACT_CRITERIA.values())


def satisfy_fact_criteria(project):
    for key in ALL_REQUIRED_KEYS:
        create_fact(
            project=project,
            fact_key=key,
            value_json=["dummy"],
            value_type=ValueType.LIST,
            source_type=SourceType.MANUAL,
        )


@pytest.mark.django_db
def test_incomplete_when_required_facts_missing():
    session = InterviewSessionFactory()
    report = evaluate_completion(session)
    assert report["complete"] is False
    assert report["criteria"]["major_devices_identified"]["satisfied"] is False


@pytest.mark.django_db
def test_incomplete_when_critical_question_unanswered():
    session = InterviewSessionFactory()
    satisfy_fact_criteria(session.project)
    QuestionFactory(code="Q-CRIT", criticality="CRITICAL")
    report = evaluate_completion(session)
    assert report["complete"] is False
    assert "Q-CRIT" in report["criteria"]["critical_requirement_coverage"]["detail"]


@pytest.mark.django_db
def test_complete_when_all_criteria_met(user):
    session = InterviewSessionFactory()
    satisfy_fact_criteria(session.project)
    report = evaluate_completion(session)
    assert report["complete"] is True

    completed = complete_session(session=session, actor=user)
    assert completed.status == "COMPLETED"
    assert completed.completed_at is not None


@pytest.mark.django_db
def test_complete_session_rejected_when_criteria_unmet(user):
    session = InterviewSessionFactory()
    with pytest.raises(DomainError) as excinfo:
        complete_session(session=session, actor=user)
    assert excinfo.value.code == "completion_criteria_not_met"
    assert excinfo.value.details["unmet_criteria"]


@pytest.mark.django_db
def test_conflicted_fact_blocks_completion():
    from apps.requirements.models import FactStatus
    from apps.requirements.services import transition_fact

    session = InterviewSessionFactory()
    satisfy_fact_criteria(session.project)
    fact = session.project.facts.first()
    transition_fact(fact=fact, new_status=FactStatus.CONFLICTED)
    report = evaluate_completion(session)
    assert report["complete"] is False
    assert report["criteria"]["no_unresolved_conflicts"]["satisfied"] is False
