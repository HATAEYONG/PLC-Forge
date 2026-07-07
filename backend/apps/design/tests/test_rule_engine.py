"""Rule Engine 테스트 (PRD §12): 매칭, 효과 실행, Hard/Recommendation, 충돌, idempotency."""

import pytest

from apps.design.models import ApprovalStatus, DesignDecision, RiskLevel
from apps.design.rule_engine import apply_rules, match_rules, override_decision
from apps.design.tests.factories import RuleFactory
from apps.knowledge.tests.factories import KnowledgeItemFactory
from apps.projects.tests.factories import ProjectFactory
from apps.requirements.models import SourceType, ValueType
from apps.requirements.services import create_fact
from core.exceptions import DomainError


@pytest.fixture
def project(db):
    return ProjectFactory()


def set_fact(project, key, value, vtype=ValueType.BOOLEAN):
    return create_fact(
        project=project,
        fact_key=key,
        value_json=value,
        value_type=vtype,
        source_type=SourceType.MANUAL,
    )


@pytest.mark.django_db
class TestMatching:
    def test_rule_matches_when_condition_true(self, project):
        RuleFactory(code="R1", conditions_json={"==": [{"var": "INVERTER_USED"}, True]})
        assert match_rules({"INVERTER_USED": True})
        assert not match_rules({"INVERTER_USED": False})


@pytest.mark.django_db
class TestApply:
    def test_effects_become_traceable_decisions(self, project):
        knowledge = KnowledgeItemFactory(code="KB-X")
        RuleFactory(
            code="R-RADAR",
            rule_type="HARD",
            conditions_json={"==": [{"var": "STEAM_PRESENT"}, True]},
            effects_json=[
                {"effect": "RECOMMEND", "subject_type": "SENSOR", "value": {"p": "RADAR"}}
            ],
            applicable_scope={"knowledge_codes": ["KB-X"]},
        )
        fact = set_fact(project, "STEAM_PRESENT", True)

        result = apply_rules(project=project)
        assert result["matched_rules"] == ["R-RADAR"]
        decision = result["decisions"][0]
        # Traceability: 조건이 참조한 Fact + 규칙 + 지식이 연결됨
        assert fact in decision.input_facts.all()
        assert decision.rules.first().code == "R-RADAR"
        assert knowledge in decision.knowledge_items.all()
        assert decision.override_allowed is False  # HARD

    def test_prd_section12_example_generates_eight_effects(self, project):
        from django.core.management import call_command

        call_command("load_knowledge")
        call_command("load_rules")
        set_fact(project, "TANK_COUNT", 3, ValueType.NUMBER)
        set_fact(project, "CONTINUOUS_LEVEL_REQUIRED", True)
        set_fact(project, "STEAM_PRESENT_DURING_CIP", True)

        result = apply_rules(project=project)
        assert "RULE-LEVEL-RADAR-STEAM" in result["matched_rules"]
        radar = [
            d for d in result["decisions"] if d.generated_by_rule.code == "RULE-LEVEL-RADAR-STEAM"
        ]
        assert len(radar) == 8  # §12 예시의 8개 효과
        # 안전 성격 효과(알람/인터록/리뷰)는 승인 필요로 승격됨
        assert any(d.approval_required for d in radar)

    def test_reapply_is_idempotent(self, project):
        RuleFactory(
            code="R-IDEM",
            conditions_json={"==": [{"var": "INVERTER_USED"}, True]},
            effects_json=[{"effect": "RECOMMEND", "subject_type": "COMM", "value": {}}],
        )
        set_fact(project, "INVERTER_USED", True)
        apply_rules(project=project)
        apply_rules(project=project)
        active = DesignDecision.objects.filter(project=project).exclude(
            approval_status=ApprovalStatus.SUPERSEDED
        )
        superseded = DesignDecision.objects.filter(
            project=project, approval_status=ApprovalStatus.SUPERSEDED
        )
        assert active.count() == 1
        assert superseded.count() == 1


@pytest.mark.django_db
class TestConflictDetection:
    def test_conflicting_values_detected(self, project):
        RuleFactory(
            code="R-A",
            priority=10,
            conditions_json={"var": "X"},
            effects_json=[
                {
                    "effect": "RECOMMEND",
                    "subject_type": "SENSOR",
                    "subject_id": "L",
                    "value": {"p": "RADAR"},
                }
            ],
        )
        RuleFactory(
            code="R-B",
            priority=5,
            conditions_json={"var": "X"},
            effects_json=[
                {
                    "effect": "RECOMMEND",
                    "subject_type": "SENSOR",
                    "subject_id": "L",
                    "value": {"p": "ULTRASONIC"},
                }
            ],
        )
        set_fact(project, "X", True)
        result = apply_rules(project=project)
        assert len(result["conflicts"]) == 1
        assert result["conflicts"][0]["subject_type"] == "SENSOR"


@pytest.mark.django_db
class TestOverride:
    def test_hard_rule_decision_cannot_be_overridden(self, project):
        RuleFactory(
            code="R-HARD",
            rule_type="HARD",
            conditions_json={"var": "X"},
            effects_json=[{"effect": "RECOMMEND", "subject_type": "S", "value": {}}],
        )
        set_fact(project, "X", True)
        decision = apply_rules(project=project)["decisions"][0]
        with pytest.raises(DomainError) as excinfo:
            override_decision(decision=decision, reason="무시하고 싶음")
        assert excinfo.value.code == "hard_rule_override_forbidden"

    def test_recommendation_decision_can_be_overridden(self, project):
        RuleFactory(
            code="R-REC",
            rule_type="RECOMMENDATION",
            conditions_json={"var": "X"},
            effects_json=[{"effect": "RECOMMEND", "subject_type": "S", "value": {}}],
        )
        set_fact(project, "X", True)
        decision = apply_rules(project=project)["decisions"][0]
        override_decision(decision=decision, reason="현장 표준과 상이")
        decision.refresh_from_db()
        assert decision.overridden is True

    def test_high_risk_effect_requires_approval(self, project):
        RuleFactory(
            code="R-ALARM",
            conditions_json={"var": "X"},
            effects_json=[
                {"effect": "REQUIRE_ALARM", "subject_type": "ALARM", "value": {"t": "HIGH"}}
            ],
        )
        set_fact(project, "X", True)
        decision = apply_rules(project=project)["decisions"][0]
        assert decision.risk_level == RiskLevel.HIGH
        assert decision.approval_required is True


@pytest.mark.django_db
def test_apply_rules_api_end_to_end(api_client, project):
    from django.core.management import call_command

    call_command("load_knowledge")
    call_command("load_rules")
    set_fact(project, "TANK_COUNT", 3, ValueType.NUMBER)
    set_fact(project, "CONTINUOUS_LEVEL_REQUIRED", True)
    set_fact(project, "STEAM_PRESENT_DURING_CIP", True)

    response = api_client.post(f"/api/projects/{project.id}/apply-rules/")
    assert response.status_code == 201
    body = response.json()
    assert "RULE-LEVEL-RADAR-STEAM" in body["matched_rules"]
    assert len(body["decisions"]) >= 8
    # 각 결정에 근거가 연결되어 있음 (Traceability)
    assert all(d["rules"] for d in body["decisions"])
