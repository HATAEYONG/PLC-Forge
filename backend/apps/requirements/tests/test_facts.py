import pytest

from apps.projects.tests.factories import ProjectFactory
from apps.requirements.models import FactStatus, ProjectFact, SourceType, ValueType
from apps.requirements.services import create_fact, transition_fact
from core.exceptions import DomainError


@pytest.fixture
def project(db):
    return ProjectFactory()


def make_fact(project, key="TANK_COUNT", value=3):
    return create_fact(
        project=project,
        fact_key=key,
        value_json=value,
        value_type=ValueType.NUMBER,
        source_type=SourceType.MANUAL,
    )


@pytest.mark.django_db
class TestFactVersioning:
    def test_first_fact_is_version_1_proposed(self, project):
        fact = make_fact(project)
        assert fact.version == 1
        assert fact.status == FactStatus.PROPOSED

    def test_recreating_same_key_supersedes_and_increments(self, project):
        first = make_fact(project)
        second = make_fact(project, value=4)
        first.refresh_from_db()
        assert second.version == 2
        assert first.status == FactStatus.SUPERSEDED


@pytest.mark.django_db
class TestFactTransitions:
    def test_proposed_to_confirmed_allowed(self, project):
        fact = make_fact(project)
        transition_fact(fact=fact, new_status=FactStatus.CONFIRMED)
        assert fact.status == FactStatus.CONFIRMED

    def test_proposed_to_superseded_rejected(self, project):
        fact = make_fact(project)
        with pytest.raises(DomainError) as excinfo:
            transition_fact(fact=fact, new_status=FactStatus.SUPERSEDED)
        assert excinfo.value.code == "invalid_fact_transition"

    def test_terminal_states_allow_no_transition(self, project):
        fact = make_fact(project)
        transition_fact(fact=fact, new_status=FactStatus.REJECTED)
        with pytest.raises(DomainError):
            transition_fact(fact=fact, new_status=FactStatus.CONFIRMED)


@pytest.mark.django_db
def test_fact_api_create_and_transition(api_client, project):
    created = api_client.post(
        "/api/facts/",
        {
            "project": str(project.id),
            "fact_key": "MAX_TEMPERATURE_APPROX",
            "value_json": 80,
            "value_type": "NUMBER",
            "unit": "C",
            "source_type": "MANUAL",
        },
        format="json",
    )
    assert created.status_code == 201
    fact_id = created.json()["id"]
    assert created.json()["status"] == "PROPOSED"

    ok = api_client.post(
        f"/api/facts/{fact_id}/transition/", {"status": "CONFIRMED"}, format="json"
    )
    assert ok.status_code == 200
    assert ok.json()["status"] == "CONFIRMED"

    bad = api_client.post(
        f"/api/facts/{fact_id}/transition/", {"status": "PROPOSED"}, format="json"
    )
    assert bad.status_code == 409
    assert bad.json()["error"]["code"] == "invalid_fact_transition"

    assert ProjectFact.objects.get(id=fact_id).status == FactStatus.CONFIRMED
