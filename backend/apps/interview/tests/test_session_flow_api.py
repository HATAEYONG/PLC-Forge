"""세션 API 확장 테스트 (next-question / facts / state / progress / complete)."""

import pytest
from django.core.management import call_command

from apps.interview.models import Question
from apps.interview.tests.factories import InterviewSessionFactory, QuestionFactory


@pytest.mark.django_db
def test_next_question_returns_selection_with_reason(api_client):
    session = InterviewSessionFactory()
    QuestionFactory(code="Q-TOP", priority=90, criticality="CRITICAL", unlocks_facts=["X"])
    response = api_client.get(f"/api/interview/sessions/{session.id}/next-question/")
    assert response.status_code == 200
    body = response.json()
    assert body["complete"] is False
    assert body["question"]["code"] == "Q-TOP"
    assert body["selection"]["total_score"] > 0
    assert body["selection"]["reason"]


@pytest.mark.django_db
def test_answer_response_includes_generated_facts(api_client):
    session = InterviewSessionFactory()
    question = QuestionFactory(question_type="INTEGER", unlocks_facts=["TANK_COUNT"])
    response = api_client.post(
        f"/api/interview/sessions/{session.id}/answer/",
        {"question": str(question.id), "raw_answer": 3},
        format="json",
    )
    assert response.status_code == 201
    body = response.json()
    assert body["generated_facts"][0]["fact_key"] == "TANK_COUNT"
    assert body["generated_facts"][0]["value_json"] == 3

    state = api_client.get(f"/api/interview/sessions/{session.id}/state/").json()
    assert state["state"]["TANK_COUNT"]["value"] == 3

    facts = api_client.get(f"/api/interview/sessions/{session.id}/facts/").json()
    assert facts["count"] == 1

    progress = api_client.get(f"/api/interview/sessions/{session.id}/progress/").json()
    assert progress["answered_count"] == 1
    assert progress["completion"]["complete"] is False


@pytest.mark.django_db
def test_complete_endpoint_rejects_unmet_criteria(api_client):
    session = InterviewSessionFactory()
    response = api_client.post(f"/api/interview/sessions/{session.id}/complete/")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "completion_criteria_not_met"


@pytest.mark.django_db
def test_load_questions_command_loads_seed_and_is_idempotent():
    from apps.interview.questions_seed import QUESTIONS

    assert len(QUESTIONS) >= 50  # PRD §28 Phase 1 목표
    assert len({entry["code"] for entry in QUESTIONS}) == len(QUESTIONS)  # 코드 중복 없음

    call_command("load_questions")
    assert Question.objects.count() == len(QUESTIONS)
    call_command("load_questions")  # 재실행해도 중복 생성 없음
    assert Question.objects.count() == len(QUESTIONS)
    # 선택지형 질문에 옵션이 생성됨
    industry_question = Question.objects.get(code="Q-IND-001")
    assert industry_question.options.count() == 5
    # SAFETY 커버리지용 질문 존재
    assert Question.objects.filter(category="SAFETY").count() >= 4
