"""Question Engine 테스트 (PRD §8.5 점수, 필터링, 선택 이유 기록)."""

import pytest

from apps.interview import engine
from apps.interview.models import QuestionSelectionLog
from apps.interview.tests.factories import InterviewSessionFactory, QuestionFactory
from apps.requirements.models import SourceType, ValueType
from apps.requirements.services import create_fact


def ctx(**kwargs):
    return engine.EngineContext(**kwargs)


@pytest.mark.django_db
class TestFiltering:
    def test_required_conditions_filter(self):
        question = QuestionFactory(required_conditions={">": [{"var": "TANK_COUNT"}, 0]})
        assert not engine.is_applicable(question, ctx(state={}))
        assert engine.is_applicable(question, ctx(state={"TANK_COUNT": 3}))

    def test_exclusion_conditions_filter(self):
        question = QuestionFactory(exclusion_conditions={"==": [{"var": "HMI_REQUIRED"}, False]})
        assert engine.is_applicable(question, ctx(state={"HMI_REQUIRED": True}))
        assert not engine.is_applicable(question, ctx(state={"HMI_REQUIRED": False}))

    def test_applicable_industries_filter(self):
        question = QuestionFactory(applicable_industries=["식품"])
        assert engine.is_applicable(question, ctx(state={}))  # 업종 미확정 시 통과
        assert engine.is_applicable(question, ctx(state={"INDUSTRY": "식품"}))
        assert not engine.is_applicable(question, ctx(state={"INDUSTRY": "수처리"}))

    def test_answered_questions_excluded(self):
        session = InterviewSessionFactory()
        question = QuestionFactory()
        context = ctx(answered_question_ids={question.id})
        assert question.id not in [q.id for q in engine.iter_candidates(context)]
        assert session  # 사용


@pytest.mark.django_db
class TestScoring:
    def test_missing_critical_fact_and_information_gain(self):
        question = QuestionFactory(
            criticality="CRITICAL", unlocks_facts=["DEVICE_LIST", "TANK_COUNT"]
        )
        total, breakdown = engine.score_question(question, ctx(state={}))
        assert breakdown["missing_critical_fact"] == engine.CRITICALITY_WEIGHTS["CRITICAL"]
        assert breakdown["information_gain"] == engine.INFO_GAIN_PER_FACT * 2
        assert total > 0

    def test_safety_bonus(self):
        question = QuestionFactory(category="SAFETY")
        _, breakdown = engine.score_question(question, ctx(state={}))
        assert breakdown["safety_risk"] == engine.SAFETY_RISK_BONUS

    def test_conflict_resolution_boost(self):
        question = QuestionFactory(unlocks_facts=["TANK_COUNT"])
        _, breakdown = engine.score_question(
            question, ctx(state={"TANK_COUNT": 3}, conflicted_keys={"TANK_COUNT"})
        )
        assert breakdown["conflict_resolution"] == engine.CONFLICT_RESOLUTION_PER_FACT

    def test_redundancy_penalty_when_all_facts_known(self):
        question = QuestionFactory(unlocks_facts=["TANK_COUNT"])
        _, breakdown = engine.score_question(question, ctx(state={"TANK_COUNT": 3}))
        assert breakdown["redundancy_penalty"] == -engine.REDUNDANCY_PENALTY

    def test_user_fatigue_penalty(self):
        question = QuestionFactory()
        _, breakdown = engine.score_question(question, ctx(answers_count=10))
        assert breakdown["user_fatigue_penalty"] == -engine.USER_FATIGUE_PER_ANSWER * 10


@pytest.mark.django_db
def test_select_next_question_picks_highest_and_logs_reason():
    session = InterviewSessionFactory()
    QuestionFactory(code="Q-LOW", priority=1, criticality="LOW", unlocks_facts=["A"])
    top = QuestionFactory(
        code="Q-TOP", priority=90, criticality="CRITICAL", unlocks_facts=["DEVICE_LIST"]
    )
    question, log = engine.select_next_question(session)
    assert question == top
    assert log.total_score > 0
    assert "base_priority" in log.score_breakdown
    assert log.reason.startswith("선택 근거:")
    assert QuestionSelectionLog.objects.filter(session=session).count() == 1


@pytest.mark.django_db
def test_conflicted_fact_prioritizes_resolving_question():
    session = InterviewSessionFactory()
    project = session.project
    create_fact(
        project=project,
        fact_key="TANK_COUNT",
        value_json=3,
        value_type=ValueType.NUMBER,
        source_type=SourceType.MANUAL,
    )
    # 모순 입력으로 충돌 유발
    from apps.requirements.models import FactStatus
    from apps.requirements.services import transition_fact

    fact = project.facts.get(fact_key="TANK_COUNT")
    transition_fact(fact=fact, new_status=FactStatus.CONFLICTED)

    QuestionFactory(code="Q-OTHER", priority=50, unlocks_facts=["OTHER"])
    resolver = QuestionFactory(code="Q-RESOLVE", priority=10, unlocks_facts=["TANK_COUNT"])
    question, log = engine.select_next_question(session)
    assert question == resolver
    assert log.score_breakdown["conflict_resolution"] > 0
