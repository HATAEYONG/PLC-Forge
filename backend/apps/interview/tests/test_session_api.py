import pytest

from apps.audit.models import AuditEvent
from apps.interview.models import SessionStatus
from apps.interview.tests.factories import InterviewSessionFactory, QuestionFactory
from apps.projects.tests.factories import ProjectFactory


@pytest.mark.django_db
def test_session_create_sets_started_by(api_client, user):
    project = ProjectFactory()
    response = api_client.post(
        "/api/interview/sessions/", {"project": str(project.id)}, format="json"
    )
    assert response.status_code == 201
    assert response.json()["started_by"] == str(user.id)
    assert response.json()["status"] == "IN_PROGRESS"


@pytest.mark.django_db
def test_answer_submission_and_listing(api_client):
    session = InterviewSessionFactory()
    question = QuestionFactory()
    response = api_client.post(
        f"/api/interview/sessions/{session.id}/answer/",
        {"question": str(question.id), "raw_answer": "탱크가 3개 있고 두 개는 80도입니다."},
        format="json",
    )
    assert response.status_code == 201
    assert AuditEvent.objects.filter(action="ANSWER_SUBMITTED").exists()

    listed = api_client.get(f"/api/interview/sessions/{session.id}/answers/")
    assert listed.status_code == 200
    assert listed.json()["count"] == 1
    assert "80도" in listed.json()["results"][0]["raw_answer"]


@pytest.mark.django_db
def test_answer_rejected_when_session_not_in_progress(api_client):
    session = InterviewSessionFactory(status=SessionStatus.COMPLETED)
    question = QuestionFactory()
    response = api_client.post(
        f"/api/interview/sessions/{session.id}/answer/",
        {"question": str(question.id), "raw_answer": "답변"},
        format="json",
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "session_not_in_progress"
