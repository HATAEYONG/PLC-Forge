from apps.audit.services import record_event
from apps.interview.models import InterviewAnswer, InterviewSession, SessionStatus
from core.exceptions import DomainError


def submit_answer(*, session: InterviewSession, question, raw_answer, actor=None):
    """인터뷰 답변을 저장한다. 답변 구조화(Fact 생성)는 Phase 2의 Answer Processor가 담당."""
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
    return answer
