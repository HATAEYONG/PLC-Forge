"""Rule Engine (PRD §12): 조건 매칭 → 효과 실행 → Traceability 있는 DesignDecision.

- Hard Rule은 자동으로 무시할 수 없다 (override_allowed=False).
- 재실행은 idempotent하다: 규칙이 이전에 생성한 미승인 Decision을 SUPERSEDED 처리한다.
- 충돌 탐지: 동일 (subject_type, subject_id)에 서로 다른 값을 지정하는 규칙을 보고한다.
"""

from django.db import transaction

from apps.audit.services import record_event
from apps.design.effects import normalize_effect
from apps.design.models import ApprovalStatus, DesignDecision, Rule, RuleType
from apps.design.services import create_design_decision
from apps.knowledge.models import KnowledgeItem
from apps.requirements.models import ProjectFact
from apps.requirements.selectors import project_state
from apps.requirements.services import ACTIVE_STATUSES
from core import jsonlogic
from core.exceptions import DomainError

# 재실행 시 대체 가능한(아직 확정되지 않은) 상태
SUPERSEDABLE_STATUSES = {ApprovalStatus.DRAFT, ApprovalStatus.IN_REVIEW}


def match_rules(state: dict):
    """조건이 충족되는 활성 규칙을 우선순위 순으로 반환한다."""
    matched = []
    for rule in Rule.objects.filter(is_active=True):
        if jsonlogic.evaluate(rule.conditions_json, state):
            matched.append(rule)
    return matched


def _referenced_facts(project, rule):
    keys = jsonlogic.referenced_vars(rule.conditions_json)
    return list(
        ProjectFact.objects.filter(project=project, fact_key__in=keys, status__in=ACTIVE_STATUSES)
    )


def _linked_knowledge(rule):
    codes = (rule.applicable_scope or {}).get("knowledge_codes", [])
    if not codes:
        return []
    return list(KnowledgeItem.objects.filter(code__in=codes, is_active=True))


def _supersede_prior(project, rule, actor):
    """규칙이 이전에 생성한 미확정 Decision을 SUPERSEDED 처리한다 (idempotent 재실행)."""
    prior = DesignDecision.objects.filter(
        project=project, generated_by_rule=rule, approval_status__in=SUPERSEDABLE_STATUSES
    )
    for decision in prior:
        decision.approval_status = ApprovalStatus.SUPERSEDED
        decision.save(update_fields=["approval_status", "updated_at"])


def detect_conflicts(decisions):
    """동일 (subject_type, subject_id)에 서로 다른 값을 지정하는 Decision 쌍을 탐지한다."""
    by_subject = {}
    conflicts = []
    for decision in decisions:
        key = (decision.subject_type, decision.subject_id)
        existing = by_subject.get(key)
        if existing is not None and existing.decision_value_json != decision.decision_value_json:
            conflicts.append(
                {
                    "subject_type": decision.subject_type,
                    "subject_id": decision.subject_id,
                    "decisions": [str(existing.id), str(decision.id)],
                    "values": [existing.decision_value_json, decision.decision_value_json],
                    "hard_rule_involved": (
                        existing.override_allowed is False or decision.override_allowed is False
                    ),
                }
            )
        else:
            by_subject[key] = decision
    return conflicts


@transaction.atomic
def apply_rules(*, project, actor=None):
    """프로젝트 상태에 규칙을 적용해 DesignDecision을 생성한다.

    반환: {"decisions": [...], "conflicts": [...], "matched_rules": [codes]}
    """
    state = project_state(project_id=project.id)
    flat_state = {key: info["value"] for key, info in state.items()}
    matched = match_rules(flat_state)

    created = []
    for rule in matched:
        _supersede_prior(project, rule, actor)
        input_facts = _referenced_facts(project, rule)
        knowledge_items = _linked_knowledge(rule)
        is_hard = rule.rule_type == RuleType.HARD

        for raw_effect in rule.effects_json or []:
            effect = normalize_effect(raw_effect)
            reason = rule.explanation_template or f"규칙 {rule.code}에 의해 생성됨"
            decision = create_design_decision(
                project=project,
                decision_type=effect["decision_type"],
                subject_type=effect["subject_type"],
                subject_id=effect["subject_id"],
                decision_value=effect["decision_value"],
                reason=reason,
                input_facts=input_facts,
                rules=[rule],
                knowledge_items=knowledge_items,
                confidence=rule.confidence,
                risk_level=effect["risk_level"],
                actor=actor,
            )
            decision.generated_by_rule = rule
            decision.override_allowed = not is_hard
            decision.save(update_fields=["generated_by_rule", "override_allowed", "updated_at"])
            created.append(decision)

    conflicts = detect_conflicts(created)
    record_event(
        actor=actor,
        action="RULES_APPLIED",
        object_type="Project",
        object_id=project.id,
        after={
            "matched_rules": [rule.code for rule in matched],
            "decisions_created": len(created),
            "conflicts": len(conflicts),
        },
    )
    return {
        "decisions": created,
        "conflicts": conflicts,
        "matched_rules": [rule.code for rule in matched],
    }


def override_decision(*, decision: DesignDecision, actor=None, reason=""):
    """Recommendation 결과를 override(무시)한다. Hard Rule 결과는 거부된다 (PRD §12)."""
    if not decision.override_allowed:
        raise DomainError(
            "Hard Rule로 생성된 설계 결정은 임의로 무시할 수 없습니다.",
            code="hard_rule_override_forbidden",
            status_code=409,
        )
    if not reason or not reason.strip():
        raise DomainError("override에는 사유가 필요합니다.", code="reason_required")
    decision.overridden = True
    decision.save(update_fields=["overridden", "updated_at"])
    record_event(
        actor=actor,
        action="DESIGN_DECISION_OVERRIDDEN",
        object_type="DesignDecision",
        object_id=decision.id,
        before={"overridden": False},
        after={"overridden": True},
        reason=reason,
    )
    return decision
