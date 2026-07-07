"""Sequence Design Engine (PRD §19). Vendor Independent 시퀀스 초안을 생성한다."""

from django.db import transaction

from apps.design.models import RiskLevel
from apps.design.services import create_design_decision
from apps.requirements.models import ProjectFact
from apps.requirements.selectors import project_state
from apps.requirements.services import ACTIVE_STATUSES
from apps.sequences.models import Sequence, SequenceStep


def _flat_state(project):
    state = project_state(project_id=project.id)
    return {key: info["value"] for key, info in state.items()}


# 자동 운전 기본 시퀀스 템플릿 (MVP): 준비 → 운전 → 정지
BASE_STEPS = [
    {
        "step_no": 1,
        "name": "준비/안전 확인",
        "entry_condition": "AUTO 모드 선택 AND 인터록 정상",
        "actions": [{"op": "CHECK", "target": "SAFETY_OK"}],
        "completion_condition": "모든 인터록 정상",
        "timeout_seconds": 30,
        "timeout_alarm": "AL_SEQ_READY_TO",
        "abort_condition": "비상정지",
        "next_step": 2,
    },
    {
        "step_no": 2,
        "name": "운전",
        "entry_condition": "준비 완료",
        "actions": [{"op": "START", "target": "PROCESS"}],
        "completion_condition": "목표 도달 OR 정지 지령",
        "timeout_seconds": None,
        "hold_condition": "일시정지 지령",
        "resume_condition": "재개 지령",
        "abort_condition": "인터록 트립",
        "next_step": 3,
        "fallback_step": 1,
    },
    {
        "step_no": 3,
        "name": "정지/마무리",
        "entry_condition": "정지 조건 충족",
        "actions": [{"op": "STOP", "target": "PROCESS"}],
        "completion_condition": "모든 구동 정지 확인",
        "timeout_seconds": 30,
        "timeout_alarm": "AL_SEQ_STOP_TO",
        "next_step": None,
    },
]


@transaction.atomic
def generate_sequence(*, project, actor=None):
    """CONTROL_MODE가 AUTO/SEMI이면 Vendor Independent 시퀀스 초안을 생성한다 (idempotent)."""
    project.sequences.all().delete()

    flat = _flat_state(project)
    if flat.get("CONTROL_MODE") not in ("AUTO", "SEMI"):
        return {"sequences": 0, "skipped": "자동/반자동 운전 아님"}

    facts = list(
        ProjectFact.objects.filter(
            project=project,
            fact_key__in=["CONTROL_MODE", "SEQUENCE_OUTLINE"],
            status__in=ACTIVE_STATUSES,
        )
    )
    decision = create_design_decision(
        project=project,
        decision_type="SEQUENCE_DESIGN",
        subject_type="SEQUENCE",
        decision_value={"template": "기본 3단계(준비-운전-정지)"},
        reason="자동/반자동 운전 요구로 Vendor Independent 시퀀스 초안 생성",
        input_facts=facts,
        risk_level=RiskLevel.MEDIUM,
        actor=actor,
    )

    sequence = Sequence.objects.create(
        project=project, decision=decision, code="SEQ_MAIN", name="메인 자동 운전"
    )
    SequenceStep.objects.bulk_create(SequenceStep(sequence=sequence, **step) for step in BASE_STEPS)
    return {"sequences": 1, "steps": len(BASE_STEPS)}
