"""Answer Processing 파이프라인 (PRD §9).

Raw Answer → Validation → Normalization → Unit Conversion → Entity Extraction
→ Fact Generation → Confidence Assignment → Contradiction Detection
→ Project State Projection(온디맨드 계산이므로 별도 단계 불필요)
"""

import jsonschema

from apps.interview.models import Question, QuestionType
from apps.requirements.models import FactStatus, ProjectFact, SourceType, ValueType
from apps.requirements.services import ACTIVE_STATUSES, create_fact, transition_fact
from core.exceptions import DomainError

from .extractors import FactDraft, extract_facts_from_text
from .units import normalize_unit_value

STRUCTURED_CONFIDENCE = 0.95

YES_VALUES = {True, "true", "yes", "y", "예", "네", "필요", "있음"}
NO_VALUES = {False, "false", "no", "n", "아니오", "아니요", "불필요", "없음"}


def validate_answer(question: Question, raw_answer):
    """1단계 Validation — answer_schema(JSON Schema)에 대해 검증한다."""
    if not question.answer_schema:
        return
    try:
        jsonschema.validate(raw_answer, question.answer_schema)
    except jsonschema.ValidationError as exc:
        raise DomainError(
            f"답변이 질문의 answer_schema를 만족하지 않습니다: {exc.message}",
            code="invalid_answer",
            details={"schema_path": list(exc.absolute_schema_path)},
        ) from exc


def normalize_answer(raw_answer):
    """2단계 Normalization — 문자열 공백 정리."""
    if isinstance(raw_answer, str):
        return raw_answer.strip()
    return raw_answer


def _to_boolean(value):
    normalized = value.strip().lower() if isinstance(value, str) else value
    if normalized in YES_VALUES:
        return True
    if normalized in NO_VALUES:
        return False
    raise DomainError(f"예/아니오 답변으로 해석할 수 없습니다: {value!r}", code="invalid_answer")


def structured_drafts(question: Question, value) -> list[FactDraft]:
    """구조화 질문 유형을 unlocks_facts의 첫 키로 직접 매핑한다."""
    if not question.unlocks_facts:
        return []
    fact_key = question.unlocks_facts[0]
    question_type = question.question_type

    if question_type == QuestionType.INTEGER:
        return [FactDraft(fact_key, int(value), ValueType.NUMBER, confidence=STRUCTURED_CONFIDENCE)]
    if question_type == QuestionType.DECIMAL:
        return [
            FactDraft(fact_key, float(value), ValueType.NUMBER, confidence=STRUCTURED_CONFIDENCE)
        ]
    if question_type in {QuestionType.YES_NO, QuestionType.CONFIRMATION}:
        return [
            FactDraft(
                fact_key, _to_boolean(value), ValueType.BOOLEAN, confidence=STRUCTURED_CONFIDENCE
            )
        ]
    if question_type == QuestionType.UNIT_VALUE:
        if not isinstance(value, dict) or "value" not in value:
            raise DomainError(
                "UNIT_VALUE 답변은 {value, unit} 객체여야 합니다.", code="invalid_answer"
            )
        normalized, unit, _original = normalize_unit_value(value["value"], value.get("unit", ""))
        return [
            FactDraft(
                fact_key,
                normalized,
                ValueType.NUMBER,
                unit=unit,
                confidence=STRUCTURED_CONFIDENCE,
            )
        ]
    if question_type in {QuestionType.MULTI_CHOICE, QuestionType.DEVICE_LIST}:
        return [FactDraft(fact_key, list(value), ValueType.LIST, confidence=STRUCTURED_CONFIDENCE)]
    if question_type in {QuestionType.SINGLE_CHOICE}:
        return [FactDraft(fact_key, value, ValueType.STRING, confidence=STRUCTURED_CONFIDENCE)]
    if question_type == QuestionType.TABLE:
        return [FactDraft(fact_key, value, ValueType.OBJECT, confidence=STRUCTURED_CONFIDENCE)]
    if question_type == QuestionType.TEXT and isinstance(value, str):
        # TEXT는 원문 보존용 Fact + 아래 Entity Extraction 결과를 함께 생성
        return [FactDraft(fact_key, value, ValueType.STRING, confidence=STRUCTURED_CONFIDENCE)]
    return []


def generate_fact(*, answer, draft: FactDraft, actor=None):
    """Fact Generation + Contradiction Detection.

    - 동일 값의 활성 Fact가 있으면 새로 만들지 않는다.
    - 다른 값의 활성 Fact가 있으면 양쪽을 CONFLICTED로 남긴다.
    """
    project = answer.session.project
    latest_active = (
        ProjectFact.objects.filter(
            project=project, fact_key=draft.fact_key, status__in=ACTIVE_STATUSES
        )
        .order_by("-version")
        .first()
    )
    if latest_active is not None and latest_active.value_json == draft.value:
        return None  # 동일 정보 — 중복 생성하지 않음

    contradiction = latest_active is not None
    if contradiction and latest_active.status != FactStatus.CONFLICTED:
        transition_fact(
            fact=latest_active,
            new_status=FactStatus.CONFLICTED,
            actor=actor,
            reason=f"새 답변과 상충: {draft.value!r}",
        )
    return create_fact(
        project=project,
        fact_key=draft.fact_key,
        value_json=draft.value,
        value_type=draft.value_type,
        unit=draft.unit,
        source_type=SourceType.ANSWER,
        source_answer=answer,
        confidence=draft.confidence,
        initial_status=FactStatus.CONFLICTED if contradiction else FactStatus.PROPOSED,
        supersede_active=not contradiction,
        actor=actor,
    )


def process_answer(answer, actor=None):
    """파이프라인 전체 실행. 생성된 ProjectFact 목록을 반환한다."""
    question = answer.question
    validate_answer(question, answer.raw_answer)
    normalized = normalize_answer(answer.raw_answer)

    drafts = structured_drafts(question, normalized)
    if isinstance(normalized, str):
        existing_keys = {draft.fact_key for draft in drafts}
        drafts += [
            draft
            for draft in extract_facts_from_text(normalized)
            if draft.fact_key not in existing_keys
        ]

    facts = []
    for draft in drafts:
        fact = generate_fact(answer=answer, draft=draft, actor=actor)
        if fact is not None:
            facts.append(fact)
    return facts
