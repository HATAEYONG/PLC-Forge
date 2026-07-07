"""Interlock Design Engine + Cause & Effect Matrix (PRD §18)."""

from django.db import transaction

from apps.interlocks.models import Interlock


@transaction.atomic
def generate_interlocks(*, project, actor=None):
    """INTERLOCK_REQUIREMENT 결정에서 구조화 Interlock을 materialize한다 (idempotent)."""
    project.interlocks.all().delete()

    created = []
    seen = set()
    decisions = project.design_decisions.filter(
        decision_type="INTERLOCK_REQUIREMENT"
    ).prefetch_related("input_facts")

    for decision in decisions:
        value = decision.decision_value_json or {}
        code = f"IL_{decision.subject_id or 'GEN'}"
        if code in seen:
            continue
        seen.add(code)
        # ESTOP 등 안전 관련 인터록은 safety_related + bypass 권한 필수 (PRD §3.5)
        is_safety = "ESTOP" in (decision.subject_id or "") or decision.risk_level in (
            "HIGH",
            "CRITICAL",
        )
        created.append(
            Interlock(
                project=project,
                decision=decision,
                code=code,
                protected_device=value.get("protected_device", decision.subject_type),
                condition=value.get("condition", decision.subject_id or ""),
                effect=value.get("effect", "STOP"),
                reset_condition=value.get("reset", "MANUAL"),
                safety_related=is_safety,
                bypass_allowed=not is_safety,
                bypass_permission="SUPERVISOR (기록 필수)" if is_safety else "",
                reason=decision.reason,
            )
        )

    Interlock.objects.bulk_create(created)
    return {"interlocks": len(created), "codes": [i.code for i in created]}


def cause_effect_matrix(*, project):
    """Cause & Effect Matrix (§18): 원인(알람 조건) × 결과(인터록 효과).

    행=Cause(알람), 열=Effect(인터록), 셀=연관 여부.
    """
    alarms = list(project.alarms.all())
    interlocks = list(project.interlocks.all())
    rows = []
    for alarm in alarms:
        effects = {}
        for interlock in interlocks:
            # 연관: 알람이 명시적으로 인터록을 참조하거나, 같은 subject를 다루는 경우
            linked = (
                alarm.related_interlock == interlock.code
                or (alarm.source and alarm.source == interlock.protected_device)
                or (
                    alarm.condition
                    and interlock.condition
                    and alarm.condition in interlock.condition
                )
            )
            effects[interlock.code] = bool(linked)
        rows.append({"cause": alarm.code, "condition": alarm.condition, "effects": effects})
    return {
        "causes": [a.code for a in alarms],
        "effects": [i.code for i in interlocks],
        "matrix": rows,
    }
