from django.db import transaction

from apps.audit.services import record_event
from apps.requirements.models import FactStatus, ProjectFact
from core.exceptions import DomainError

# FactStatus 상태기계. SUPERSEDED/REJECTED는 종료 상태다.
ALLOWED_TRANSITIONS = {
    FactStatus.PROPOSED: {FactStatus.CONFIRMED, FactStatus.CONFLICTED, FactStatus.REJECTED},
    FactStatus.CONFLICTED: {FactStatus.CONFIRMED, FactStatus.REJECTED},
    FactStatus.CONFIRMED: {FactStatus.SUPERSEDED, FactStatus.CONFLICTED},
    FactStatus.SUPERSEDED: set(),
    FactStatus.REJECTED: set(),
}

# 새 버전이 생기면 대체되는 "활성" 상태
ACTIVE_STATUSES = {FactStatus.PROPOSED, FactStatus.CONFIRMED, FactStatus.CONFLICTED}


@transaction.atomic
def create_fact(
    *,
    project,
    fact_key,
    value_json,
    value_type,
    unit="",
    source_type,
    source_answer=None,
    confidence=1.0,
    initial_status=FactStatus.PROPOSED,
    supersede_active=True,
    actor=None,
):
    """Fact를 생성한다.

    supersede_active=True(기본)이면 동일 fact_key의 활성 Fact를 SUPERSEDED 처리한다.
    모순 감지 경로에서는 supersede_active=False + initial_status=CONFLICTED로
    양쪽 Fact를 충돌 상태로 남긴다 (PRD §9 Contradiction Detection).
    """
    existing = (
        ProjectFact.objects.select_for_update()
        .filter(project=project, fact_key=fact_key)
        .order_by("-version")
    )
    latest = existing.first()
    version = (latest.version + 1) if latest else 1

    if supersede_active:
        for fact in existing.filter(status__in=ACTIVE_STATUSES):
            fact.status = FactStatus.SUPERSEDED
            fact.save(update_fields=["status", "updated_at"])

    fact = ProjectFact.objects.create(
        project=project,
        fact_key=fact_key,
        value_json=value_json,
        value_type=value_type,
        unit=unit,
        source_type=source_type,
        source_answer=source_answer,
        confidence=confidence,
        status=initial_status,
        version=version,
    )
    record_event(
        actor=actor,
        action="FACT_CREATED",
        object_type="ProjectFact",
        object_id=fact.id,
        after={"fact_key": fact_key, "value": value_json, "version": version},
    )
    return fact


def transition_fact(*, fact: ProjectFact, new_status: str, actor=None, reason=""):
    """FactStatus 상태 전이. 허용되지 않은 전이는 거부한다."""
    allowed = ALLOWED_TRANSITIONS.get(FactStatus(fact.status), set())
    if new_status not in allowed:
        raise DomainError(
            f"'{fact.status}' 상태에서 '{new_status}' 상태로 전이할 수 없습니다.",
            code="invalid_fact_transition",
            status_code=409,
            details={"from": fact.status, "to": new_status, "allowed": sorted(allowed)},
        )
    before = fact.status
    fact.status = new_status
    fact.save(update_fields=["status", "updated_at"])
    record_event(
        actor=actor,
        action="FACT_TRANSITIONED",
        object_type="ProjectFact",
        object_id=fact.id,
        before={"status": before},
        after={"status": new_status},
        reason=reason,
    )
    return fact
