import pytest

from apps.audit.models import AuditEvent
from apps.design.models import RiskLevel
from apps.design.services import create_design_decision
from apps.design.tests.factories import RuleFactory
from apps.knowledge.tests.factories import KnowledgeItemFactory
from apps.projects.tests.factories import ProjectFactory
from apps.requirements.models import SourceType, ValueType
from apps.requirements.services import create_fact
from core.exceptions import DomainError


@pytest.fixture
def project(db):
    return ProjectFactory()


@pytest.fixture
def fact(project):
    return create_fact(
        project=project,
        fact_key="STEAM_PRESENT_DURING_CIP",
        value_json=True,
        value_type=ValueType.BOOLEAN,
        source_type=SourceType.MANUAL,
    )


@pytest.mark.django_db
class TestDecisionTraceability:
    def test_decision_without_any_evidence_rejected(self, project):
        with pytest.raises(DomainError) as excinfo:
            create_design_decision(
                project=project,
                decision_type="SENSOR_PRINCIPLE",
                decision_value={"principle": "RADAR"},
                reason="증기 환경",
            )
        assert excinfo.value.code == "traceability_required"

    def test_decision_without_reason_rejected(self, project, fact):
        with pytest.raises(DomainError) as excinfo:
            create_design_decision(
                project=project,
                decision_type="SENSOR_PRINCIPLE",
                decision_value={"principle": "RADAR"},
                reason="  ",
                input_facts=[fact],
            )
        assert excinfo.value.code == "reason_required"

    def test_decision_with_full_traceability(self, project, fact):
        rule = RuleFactory()
        knowledge = KnowledgeItemFactory()
        decision = create_design_decision(
            project=project,
            decision_type="SENSOR_PRINCIPLE",
            decision_value={"principle": "RADAR"},
            reason="증기 환경에서 비접촉 연속 측정이 필요하므로 레이더를 선정",
            input_facts=[fact],
            rules=[rule],
            knowledge_items=[knowledge],
        )
        assert list(decision.input_facts.all()) == [fact]
        assert list(decision.rules.all()) == [rule]
        assert list(decision.knowledge_items.all()) == [knowledge]
        assert decision.approval_required is False
        assert AuditEvent.objects.filter(
            action="DESIGN_DECISION_CREATED", object_id=str(decision.id)
        ).exists()

    def test_high_risk_decision_requires_approval(self, project, fact):
        decision = create_design_decision(
            project=project,
            decision_type="INTERLOCK",
            decision_value={"interlock": "HIGH_TEMP_TRIP"},
            reason="과열 보호",
            input_facts=[fact],
            risk_level=RiskLevel.CRITICAL,
        )
        assert decision.approval_required is True
        assert decision.approval_status == "DRAFT"


@pytest.mark.django_db
def test_decision_api_create_and_reject_without_evidence(api_client, project, fact):
    ok = api_client.post(
        "/api/design-decisions/",
        {
            "project": str(project.id),
            "decision_type": "SENSOR_PRINCIPLE",
            "decision_value": {"principle": "RADAR"},
            "reason": "증기 환경 비접촉 측정",
            "input_facts": [str(fact.id)],
        },
        format="json",
    )
    assert ok.status_code == 201
    assert ok.json()["input_facts"] == [str(fact.id)]

    bad = api_client.post(
        "/api/design-decisions/",
        {
            "project": str(project.id),
            "decision_type": "SENSOR_PRINCIPLE",
            "decision_value": {"principle": "RADAR"},
            "reason": "근거 없음",
        },
        format="json",
    )
    assert bad.status_code == 400
    assert bad.json()["error"]["code"] == "traceability_required"
