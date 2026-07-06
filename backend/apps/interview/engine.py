"""Question Engine (PRD §8): 후보 필터링 → 점수화(§8.5) → 선택 + 선택 이유 기록.

가중치는 콜드스타트 초기값이다 (RISKS.md R3). QuestionSelectionLog에 점수 내역을
남겨 추후 KPI(§28) 기반으로 튜닝한다.
"""

from dataclasses import dataclass, field

from apps.interview.models import Question, QuestionCategory, QuestionSelectionLog
from apps.requirements import selectors as fact_selectors
from apps.requirements.models import FactStatus
from core import jsonlogic

# ── §8.5 점수 가중치 ──────────────────────────────────────
CRITICALITY_WEIGHTS = {"CRITICAL": 100.0, "HIGH": 50.0, "MEDIUM": 20.0, "LOW": 5.0}
SAFETY_RISK_BONUS = 40.0
INFO_GAIN_PER_FACT = 10.0
DESIGN_UNLOCK_PER_DECISION = 5.0
CONFLICT_RESOLUTION_PER_FACT = 60.0
DOWNSTREAM_IMPACT_BY_CATEGORY = {
    QuestionCategory.PROCESS: 15.0,
    QuestionCategory.DEVICE: 15.0,
    QuestionCategory.SENSOR: 10.0,
    QuestionCategory.SAFETY: 10.0,
    QuestionCategory.PLC: 5.0,
    QuestionCategory.COMMUNICATION: 5.0,
}
REDUNDANCY_PENALTY = 30.0
USER_FATIGUE_PER_ANSWER = 0.5

COMPONENT_LABELS = {
    "base_priority": "기본 우선순위",
    "missing_critical_fact": "핵심 정보 누락",
    "safety_risk": "안전 위험 탐지",
    "information_gain": "신규 정보 획득",
    "design_unlock": "설계 단계 해제",
    "conflict_resolution": "충돌 해소",
    "downstream_impact": "하위 설계 영향",
    "redundancy_penalty": "중복 정보",
    "user_fatigue_penalty": "사용자 피로도",
}


@dataclass
class EngineContext:
    """세션 시점의 프로젝트 상태 스냅샷."""

    state: dict = field(default_factory=dict)  # fact_key -> value (활성 Fact)
    conflicted_keys: set = field(default_factory=set)
    answered_question_ids: set = field(default_factory=set)
    answers_count: int = 0


def build_context(session) -> EngineContext:
    projection = fact_selectors.project_state(project_id=session.project_id)
    state = {key: info["value"] for key, info in projection.items()}
    conflicted_keys = set(
        fact_selectors.facts_for_project(project_id=session.project_id)
        .filter(status=FactStatus.CONFLICTED)
        .values_list("fact_key", flat=True)
    )
    answered_ids = set(session.answers.values_list("question_id", flat=True))
    return EngineContext(
        state=state,
        conflicted_keys=conflicted_keys,
        answered_question_ids=answered_ids,
        answers_count=len(answered_ids),
    )


def is_applicable(question: Question, context: EngineContext) -> bool:
    """Not Applicable 판정 — required/exclusion/업종/공정 조건 (§8.2)."""
    if question.required_conditions and not jsonlogic.evaluate(
        question.required_conditions, context.state
    ):
        return False
    if question.exclusion_conditions and jsonlogic.evaluate(
        question.exclusion_conditions, context.state
    ):
        return False

    industry = context.state.get("INDUSTRY")
    if question.applicable_industries and industry is not None:
        if industry not in question.applicable_industries:
            return False

    processes = context.state.get("PROCESSES")
    if question.applicable_processes and processes is not None:
        if not set(question.applicable_processes) & set(processes):
            return False
    return True


def iter_candidates(context: EngineContext):
    """Already Answered / Not Applicable 질문을 제외한 후보를 반환한다."""
    for question in Question.objects.filter(is_active=True):
        if question.id in context.answered_question_ids:
            continue
        if not is_applicable(question, context):
            continue
        yield question


def score_question(question: Question, context: EngineContext):
    """§8.5 점수 계산. (총점, 요소별 내역)을 반환한다."""
    unlock_facts = set(question.unlocks_facts or [])
    # 충돌(CONFLICTED) 상태의 Fact는 신뢰할 수 없으므로 "확보된 정보"로 취급하지 않는다.
    reliable_keys = set(context.state) - context.conflicted_keys
    missing_facts = unlock_facts - reliable_keys
    is_safety = question.category == QuestionCategory.SAFETY or "SAFETY" in (
        question.risk_detection_tags or []
    )

    breakdown = {
        "base_priority": float(question.priority),
        "missing_critical_fact": (
            CRITICALITY_WEIGHTS.get(question.criticality, 0.0) if missing_facts else 0.0
        ),
        "safety_risk": SAFETY_RISK_BONUS if is_safety else 0.0,
        "information_gain": INFO_GAIN_PER_FACT * len(missing_facts),
        "design_unlock": DESIGN_UNLOCK_PER_DECISION * len(question.unlocks_decisions or []),
        "conflict_resolution": CONFLICT_RESOLUTION_PER_FACT
        * len(unlock_facts & context.conflicted_keys),
        "downstream_impact": DOWNSTREAM_IMPACT_BY_CATEGORY.get(question.category, 0.0),
        "redundancy_penalty": (-REDUNDANCY_PENALTY if unlock_facts and not missing_facts else 0.0),
        "user_fatigue_penalty": -USER_FATIGUE_PER_ANSWER * context.answers_count,
    }
    return sum(breakdown.values()), breakdown


def _selection_reason(breakdown: dict) -> str:
    contributions = [
        (COMPONENT_LABELS.get(key, key), value) for key, value in breakdown.items() if value > 0
    ]
    contributions.sort(key=lambda item: -item[1])
    top = ", ".join(f"{label}(+{value:g})" for label, value in contributions[:3])
    return f"선택 근거: {top}" if top else "선택 근거: 기본 우선순위"


def select_next_question(session):
    """최고 점수 질문을 선택하고 QuestionSelectionLog에 이유를 남긴다."""
    context = build_context(session)
    best_question, best_score, best_breakdown = None, None, None
    for question in iter_candidates(context):
        total, breakdown = score_question(question, context)
        if best_score is None or total > best_score:
            best_question, best_score, best_breakdown = question, total, breakdown

    if best_question is None:
        return None

    log = QuestionSelectionLog.objects.create(
        session=session,
        question=best_question,
        total_score=best_score,
        score_breakdown=best_breakdown,
        reason=_selection_reason(best_breakdown),
    )
    return best_question, log
