from django.db import transaction
from django.utils import timezone

from apps.audit.services import record_event
from apps.interview.models import InterviewAnswer, InterviewSession, SessionStatus
from apps.interview.processing.pipeline import process_answer
from core.exceptions import DomainError


@transaction.atomic
def submit_answer(*, session: InterviewSession, question, raw_answer, actor=None):
    """인터뷰 답변을 저장하고 Answer Processing 파이프라인(§9)을 실행한다.

    반환: (answer, 생성된 ProjectFact 목록)
    """
    if session.status != SessionStatus.IN_PROGRESS:
        raise DomainError(
            "진행 중인 인터뷰 세션에만 답변할 수 있습니다.",
            code="session_not_in_progress",
            status_code=409,
        )
    answer = InterviewAnswer.objects.create(
        session=session,
        question=question,
        raw_answer=raw_answer,
        answered_by=actor if actor is not None and actor.is_authenticated else None,
    )
    record_event(
        actor=answer.answered_by,
        action="ANSWER_SUBMITTED",
        object_type="InterviewAnswer",
        object_id=answer.id,
        after={"question": question.code, "raw_answer": raw_answer},
    )
    facts = process_answer(answer, actor=answer.answered_by)
    return answer, facts


def complete_session(*, session: InterviewSession, actor=None):
    """종료조건(§8.6) 충족 시 세션을 COMPLETED로 전환한다. Human Approval 관점에서
    자동 완료하지 않고 명시적 호출로만 완료한다."""
    from apps.interview.completion import evaluate_completion

    if session.status != SessionStatus.IN_PROGRESS:
        raise DomainError(
            "진행 중인 세션만 완료할 수 있습니다.",
            code="session_not_in_progress",
            status_code=409,
        )
    report = evaluate_completion(session)
    if not report["complete"]:
        unmet = [name for name, item in report["criteria"].items() if not item["satisfied"]]
        raise DomainError(
            "종료조건이 충족되지 않았습니다.",
            code="completion_criteria_not_met",
            status_code=409,
            details={"unmet_criteria": unmet},
        )
    session.status = SessionStatus.COMPLETED
    session.completed_at = timezone.now()
    session.save(update_fields=["status", "completed_at", "updated_at"])
    record_event(
        actor=actor,
        action="INTERVIEW_COMPLETED",
        object_type="InterviewSession",
        object_id=session.id,
    )
    return session
