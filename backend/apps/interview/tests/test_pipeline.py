"""Answer Processing 파이프라인 테스트 (PRD §9 시나리오 포함)."""

import pytest

from apps.interview.services import submit_answer
from apps.interview.tests.factories import InterviewSessionFactory, QuestionFactory
from apps.requirements.models import FactStatus, ProjectFact
from core.exceptions import DomainError

SCENARIO_TEXT = "탱크가 3개 있고 그중 두 개는 80도 정도이며 세척할 때 증기가 생깁니다."


@pytest.mark.django_db
def test_prd_scenario_generates_five_facts(user):
    """PRD §9 예시: 자연어 답변 → 구조화 Fact 5종 (LLM 미사용)."""
    session = InterviewSessionFactory()
    question = QuestionFactory(
        question_type="TEXT", unlocks_facts=["TANK_ENVIRONMENT"], code="Q-SEN-003"
    )
    _answer, facts = submit_answer(
        session=session, question=question, raw_answer=SCENARIO_TEXT, actor=user
    )
    by_key = {fact.fact_key: fact for fact in facts}

    assert by_key["TANK_COUNT"].value_json == 3
    assert by_key["HEATED_TANK_COUNT"].value_json == 2
    assert by_key["MAX_TEMPERATURE_APPROX"].value_json == 80
    assert by_key["MAX_TEMPERATURE_APPROX"].unit == "C"
    assert by_key["STEAM_PRESENT_DURING_CIP"].value_json is True
    assert by_key["CIP_REQUIRED"].value_json is True
    # 원본 답변과 Fact의 연결 유지 (PRD §9)
    assert all(fact.source_answer_id == _answer.id for fact in facts)
    assert all(fact.confidence < 1.0 for fact in facts)


@pytest.mark.django_db
def test_structured_answer_maps_to_unlock_fact(user):
    session = InterviewSessionFactory()
    question = QuestionFactory(
        question_type="INTEGER",
        unlocks_facts=["TANK_COUNT"],
        answer_schema={"type": "integer", "minimum": 0},
    )
    _answer, facts = submit_answer(session=session, question=question, raw_answer=3, actor=user)
    assert len(facts) == 1
    assert facts[0].fact_key == "TANK_COUNT"
    assert facts[0].value_json == 3
    assert facts[0].status == FactStatus.PROPOSED


@pytest.mark.django_db
def test_answer_schema_validation_rejects_bad_answer(user):
    session = InterviewSessionFactory()
    question = QuestionFactory(
        question_type="INTEGER",
        unlocks_facts=["TANK_COUNT"],
        answer_schema={"type": "integer", "minimum": 0},
    )
    with pytest.raises(DomainError) as excinfo:
        submit_answer(session=session, question=question, raw_answer="셋", actor=user)
    assert excinfo.value.code == "invalid_answer"


@pytest.mark.django_db
def test_unit_value_fahrenheit_converted(user):
    session = InterviewSessionFactory()
    question = QuestionFactory(question_type="UNIT_VALUE", unlocks_facts=["MAX_TEMPERATURE_APPROX"])
    _answer, facts = submit_answer(
        session=session,
        question=question,
        raw_answer={"value": 176, "unit": "F"},
        actor=user,
    )
    assert facts[0].value_json == 80.0
    assert facts[0].unit == "C"


@pytest.mark.django_db
class TestContradictionDetection:
    def test_conflicting_answer_marks_both_conflicted(self, user):
        session = InterviewSessionFactory()
        question = QuestionFactory(question_type="INTEGER", unlocks_facts=["TANK_COUNT"])
        submit_answer(session=session, question=question, raw_answer=3, actor=user)
        _answer, facts = submit_answer(session=session, question=question, raw_answer=5, actor=user)
        assert facts[0].status == FactStatus.CONFLICTED
        versions = ProjectFact.objects.filter(
            project=session.project, fact_key="TANK_COUNT"
        ).order_by("version")
        assert [fact.status for fact in versions] == [
            FactStatus.CONFLICTED,
            FactStatus.CONFLICTED,
        ]

    def test_same_value_answer_does_not_duplicate(self, user):
        session = InterviewSessionFactory()
        question = QuestionFactory(question_type="INTEGER", unlocks_facts=["TANK_COUNT"])
        submit_answer(session=session, question=question, raw_answer=3, actor=user)
        _answer, facts = submit_answer(session=session, question=question, raw_answer=3, actor=user)
        assert facts == []
        assert ProjectFact.objects.filter(fact_key="TANK_COUNT").count() == 1
