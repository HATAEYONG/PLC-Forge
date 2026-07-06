import pytest

from apps.interview.models import AnswerOption
from apps.interview.tests.factories import QuestionFactory

FULL_QUESTION = {
    "code": "Q-SAFETY-001",
    "version": 1,
    "text": "비상정지 버튼이 필요한 위치는 어디입니까?",
    "help_text": "작업자 접근 지점을 기준으로 답해주세요.",
    "category": "SAFETY",
    "question_type": "TEXT",
    "answer_schema": {"type": "string", "minLength": 1},
    "priority": 100,
    "criticality": "CRITICAL",
    "required_conditions": {"==": [{"var": "HAS_MOVING_EQUIPMENT"}, True]},
    "exclusion_conditions": {},
    "applicable_industries": ["식품", "수처리"],
    "applicable_processes": ["Conveyor Transfer"],
    "unlocks_facts": ["ESTOP_LOCATIONS"],
    "unlocks_decisions": ["SAFETY_IO_SIZING"],
    "risk_detection_tags": ["SAFETY"],
    "is_active": True,
}


@pytest.mark.django_db
def test_question_create_with_full_prd_fields(api_client):
    response = api_client.post("/api/questions/", FULL_QUESTION, format="json")
    assert response.status_code == 201
    body = response.json()
    for field, expected in FULL_QUESTION.items():
        assert body[field] == expected, field


@pytest.mark.django_db
def test_question_invalid_answer_schema_rejected(api_client):
    payload = {**FULL_QUESTION, "answer_schema": {"type": 123}}
    response = api_client.post("/api/questions/", payload, format="json")
    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert "answer_schema" in body["error"]["details"]


@pytest.mark.django_db
def test_question_duplicate_code_version_rejected(api_client):
    QuestionFactory(code="Q-DUP", version=1)
    payload = {**FULL_QUESTION, "code": "Q-DUP", "version": 1}
    response = api_client.post("/api/questions/", payload, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_question_options_ordered(api_client):
    question = QuestionFactory(question_type="SINGLE_CHOICE")
    AnswerOption.objects.create(question=question, value="B", label="라다", order=2)
    AnswerOption.objects.create(question=question, value="A", label="초음파", order=1)
    response = api_client.get(f"/api/questions/{question.id}/")
    values = [option["value"] for option in response.json()["options"]]
    assert values == ["A", "B"]
