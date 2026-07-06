"""인터뷰 종료조건 평가 (PRD §8.6).

단순히 모든 질문을 소진했다고 종료하지 않는다. 설계 착수 가능성(Design Readiness)을
기준별로 평가하고, 하나라도 미충족이면 인터뷰를 계속한다.

Fact 키 기준은 MVP 초기값이며 Phase 3~4에서 지식베이스와 연동해 정교화한다.
"""

from apps.interview.engine import build_context, is_applicable
from apps.interview.models import Criticality, Question, QuestionCategory

# 설계 산출물별 최소 필요 Fact (§8.6 3~9항의 MVP 정의)
REQUIRED_FACT_CRITERIA = {
    "major_devices_identified": {"DEVICE_LIST"},
    "sensor_requirements_identified": {"MEASUREMENT_REQUIREMENTS"},
    "io_estimation_possible": {"DEVICE_LIST", "MEASUREMENT_REQUIREMENTS"},
    "plc_sizing_possible": {"DEVICE_LIST", "CONTROL_MODE"},
    "communication_architecture_possible": {"CONTROL_MODE", "HMI_REQUIRED"},
    "hmi_minimum_screen_set_possible": {"HMI_REQUIRED", "DEVICE_LIST"},
    "alarm_interlock_draft_possible": {"DEVICE_LIST", "SAFETY_REQUIREMENTS"},
}


def _question_coverage(context, *, category=None, criticality=None):
    """적용 가능한(applicable) 질문 중 아직 답변되지 않은 질문 코드 목록."""
    questions = Question.objects.filter(is_active=True)
    if category:
        questions = questions.filter(category=category)
    if criticality:
        questions = questions.filter(criticality=criticality)
    unanswered = []
    for question in questions:
        if question.id in context.answered_question_ids:
            continue
        if not is_applicable(question, context):
            continue
        unanswered.append(question.code)
    return unanswered


def evaluate_completion(session) -> dict:
    """종료조건 리포트. {"complete": bool, "criteria": {기준: {satisfied, detail}}}"""
    context = build_context(session)
    known_keys = set(context.state)
    criteria = {}

    unanswered_critical = _question_coverage(context, criticality=Criticality.CRITICAL)
    criteria["critical_requirement_coverage"] = {
        "satisfied": not unanswered_critical,
        "detail": (
            "모든 CRITICAL 질문 답변 완료"
            if not unanswered_critical
            else f"미답변 CRITICAL 질문: {', '.join(unanswered_critical)}"
        ),
    }

    unanswered_safety = _question_coverage(context, category=QuestionCategory.SAFETY)
    criteria["safety_question_coverage"] = {
        "satisfied": not unanswered_safety,
        "detail": (
            "모든 SAFETY 질문 답변 완료"
            if not unanswered_safety
            else f"미답변 SAFETY 질문: {', '.join(unanswered_safety)}"
        ),
    }

    for criterion, required_keys in REQUIRED_FACT_CRITERIA.items():
        missing = required_keys - known_keys
        criteria[criterion] = {
            "satisfied": not missing,
            "detail": (
                "필요 정보 확보됨" if not missing else f"누락 Fact: {', '.join(sorted(missing))}"
            ),
        }

    criteria["no_unresolved_conflicts"] = {
        "satisfied": not context.conflicted_keys,
        "detail": (
            "미해결 충돌 없음"
            if not context.conflicted_keys
            else f"충돌 상태 Fact: {', '.join(sorted(context.conflicted_keys))}"
        ),
    }

    return {
        "complete": all(item["satisfied"] for item in criteria.values()),
        "criteria": criteria,
    }
