import pytest

from apps.audit.models import AuditEvent
from apps.projects.tests.factories import ProjectFactory
from apps.requirements.models import FactStatus, SourceType, ValueType
from apps.requirements.services import create_fact, transition_fact


@pytest.mark.django_db
def test_fact_lifecycle_is_audited(user):
    project = ProjectFactory()
    fact = create_fact(
        project=project,
        fact_key="CIP_REQUIRED",
        value_json=True,
        value_type=ValueType.BOOLEAN,
        source_type=SourceType.MANUAL,
        actor=user,
    )
    transition_fact(fact=fact, new_status=FactStatus.CONFIRMED, actor=user, reason="고객 확인")

    created_event = AuditEvent.objects.get(action="FACT_CREATED", object_id=str(fact.id))
    assert created_event.actor == user
    assert created_event.after_json["fact_key"] == "CIP_REQUIRED"

    transition_event = AuditEvent.objects.get(action="FACT_TRANSITIONED", object_id=str(fact.id))
    assert transition_event.before_json == {"status": "PROPOSED"}
    assert transition_event.after_json == {"status": "CONFIRMED"}
    assert transition_event.reason == "고객 확인"


@pytest.mark.django_db
def test_audit_events_are_read_only_api(api_client):
    response = api_client.post("/api/audit-events/", {}, format="json")
    assert response.status_code == 405
