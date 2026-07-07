"""Rule Engine의 Effect 어휘와 Executor (PRD §12).

규칙의 effects_json은 effect 객체의 목록이다. 각 effect는 하나의 DesignDecision으로
실행된다. §12 예시 규칙의 효과들을 표현할 수 있어야 한다:

    Recommend Radar Level Measurement Principle → RECOMMEND
    Require Analog Input                         → REQUIRE
    Require High/Low Level Alarm                 → REQUIRE_ALARM
    Require Overflow Protection Review           → REVIEW
    Require HMI Trend                            → REQUIRE
    Generate FAT/SAT Test                        → GENERATE_TEST

effect 형식:
    {"effect": "RECOMMEND", "subject_type": "SENSOR_PRINCIPLE",
     "subject_id": "LEVEL", "value": {...}, "risk_level": "MEDIUM"}
"""

from apps.design.models import RiskLevel
from core.exceptions import DomainError

# effect 유형 → 생성될 DesignDecision.decision_type
EFFECT_DECISION_TYPES = {
    "RECOMMEND": "RECOMMENDATION",
    "REQUIRE": "REQUIREMENT",
    "REQUIRE_ALARM": "ALARM_REQUIREMENT",
    "REQUIRE_INTERLOCK": "INTERLOCK_REQUIREMENT",
    "REVIEW": "REVIEW_ITEM",
    "GENERATE_TEST": "TEST_REQUIREMENT",
}

# Safety 성격의 effect는 최소 위험도를 HIGH로 승격 (Human Approval 유도, PRD §3.5)
SAFETY_EFFECTS = {"REQUIRE_ALARM", "REQUIRE_INTERLOCK", "REVIEW"}


def normalize_effect(effect: dict) -> dict:
    """effect 유형을 검증하고 decision_type/risk_level을 정규화한다."""
    if not isinstance(effect, dict) or "effect" not in effect:
        raise DomainError("effect는 'effect' 키를 가진 객체여야 합니다.", code="invalid_effect")
    effect_type = effect["effect"]
    if effect_type not in EFFECT_DECISION_TYPES:
        raise DomainError(f"지원하지 않는 effect 유형: '{effect_type}'", code="unknown_effect")

    risk_level = effect.get("risk_level")
    if risk_level is None:
        risk_level = RiskLevel.HIGH if effect_type in SAFETY_EFFECTS else RiskLevel.LOW

    return {
        "decision_type": EFFECT_DECISION_TYPES[effect_type],
        "subject_type": effect.get("subject_type", effect_type),
        "subject_id": str(effect.get("subject_id", "")),
        "decision_value": effect.get("value", {}),
        "risk_level": risk_level,
    }
