"""Alarm Design Engine (PRD §18).

Rule Engine이 만든 ALARM_REQUIREMENT 결정과 CRITICAL_ALARMS Fact를 구조화 Alarm으로
materialize한다. 통신 링크의 통신 알람도 포함한다.
"""

from django.db import transaction

from apps.alarms.models import Alarm, AlarmPriority, ResetType
from apps.requirements.selectors import project_state


def _flat_state(project):
    state = project_state(project_id=project.id)
    return {key: info["value"] for key, info in state.items()}


@transaction.atomic
def generate_alarms(*, project, actor=None):
    """설계 결정과 Fact로 Alarm을 생성한다 (idempotent)."""
    project.alarms.all().delete()

    created = []
    seen_codes = set()

    def add(code, **kwargs):
        if code in seen_codes:
            return
        seen_codes.add(code)
        created.append(Alarm(project=project, code=code, **kwargs))

    # 1) Rule Engine의 ALARM_REQUIREMENT 결정에서 materialize
    alarm_decisions = project.design_decisions.filter(
        decision_type="ALARM_REQUIREMENT"
    ).prefetch_related("input_facts")
    for decision in alarm_decisions:
        value = decision.decision_value_json or {}
        alarm_type = value.get("type", decision.subject_id or "ALARM")
        priority = value.get("priority", AlarmPriority.HIGH)
        code = f"AL_{decision.subject_id or alarm_type}"
        add(
            code,
            decision=decision,
            source=decision.subject_type,
            condition=alarm_type,
            priority=priority if priority in AlarmPriority.values else AlarmPriority.HIGH,
            message=f"{alarm_type} 알람",
            reset_type=ResetType.MANUAL,
            latching=True,
        )

    # 2) 통신 링크 → 통신 알람 (§16 Communication Alarm)
    for link in project.comm_links.filter(comm_alarm=True).select_related("target"):
        add(
            f"AL_COMM_{link.target.name}".replace(" ", "_"),
            source="COMMUNICATION",
            condition=f"{link.target.name} 통신 두절",
            priority=AlarmPriority.HIGH,
            message=f"{link.target.name} 통신 이상",
            reset_type=ResetType.AUTO,
        )

    Alarm.objects.bulk_create(created)
    return {"alarms": len(created), "codes": [a.code for a in created]}
