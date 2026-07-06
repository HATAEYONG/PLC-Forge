from django.db import transaction

from apps.audit.services import record_event
from apps.design.models import DesignDecision, RiskLevel
from core.exceptions import DomainError

# Safety 관련 결정은 승인 필수 (PRD §3.5)
APPROVAL_REQUIRED_RISK_LEVELS = {RiskLevel.HIGH, RiskLevel.CRITICAL}


@transaction.atomic
def create_design_decision(
    *,
    project,
    decision_type,
    decision_value,
    reason,
    input_facts=(),
    rules=(),
    knowledge_items=(),
    subject_type="",
    subject_id="",
    confidence=1.0,
    risk_level=RiskLevel.LOW,
    actor=None,
):
    """DesignDecision을 생성한다. Traceability 근거가 없으면 거부한다 (PRD §3.4, §33-11)."""
    if not reason or not reason.strip():
        raise DomainError(
            "설계 결정에는 결정 이유(reason)가 반드시 필요합니다.",
            code="reason_required",
        )
    if not (input_facts or rules or knowledge_items):
        raise DomainError(
            "설계 결정에는 최소 1개의 근거(입력 Fact, 규칙 또는 지식 항목)가 필요합니다.",
            code="traceability_required",
        )

    approval_required = RiskLevel(risk_level) in APPROVAL_REQUIRED_RISK_LEVELS

    decision = DesignDecision.objects.create(
        project=project,
        decision_type=decision_type,
        subject_type=subject_type,
        subject_id=subject_id,
        decision_value_json=decision_value,
        reason=reason,
        confidence=confidence,
        risk_level=risk_level,
        approval_required=approval_required,
    )
    decision.input_facts.set(input_facts)
    decision.rules.set(rules)
    decision.knowledge_items.set(knowledge_items)

    record_event(
        actor=actor,
        action="DESIGN_DECISION_CREATED",
        object_type="DesignDecision",
        object_id=decision.id,
        after={
            "decision_type": decision_type,
            "value": decision_value,
            "risk_level": str(risk_level),
        },
        reason=reason,
    )
    return decision
