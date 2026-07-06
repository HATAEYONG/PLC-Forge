from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.interview import engine, services
from apps.interview.completion import evaluate_completion
from apps.interview.models import AnswerOption, InterviewSession, Question
from apps.interview.serializers import (
    AnswerOptionSerializer,
    AnswerSubmitSerializer,
    InterviewAnswerSerializer,
    InterviewSessionSerializer,
    QuestionSerializer,
)
from apps.requirements import selectors as fact_selectors
from apps.requirements.serializers import ProjectFactSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.prefetch_related("options")
    serializer_class = QuestionSerializer


class AnswerOptionViewSet(viewsets.ModelViewSet):
    queryset = AnswerOption.objects.all()
    serializer_class = AnswerOptionSerializer


class InterviewSessionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = InterviewSession.objects.select_related("project")
    serializer_class = InterviewSessionSerializer

    def perform_create(self, serializer):
        serializer.save(started_by=self.request.user)

    @action(detail=True, methods=["post"])
    def answer(self, request, pk=None):
        session = self.get_object()
        serializer = AnswerSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answer, facts = services.submit_answer(
            session=session,
            question=serializer.validated_data["question"],
            raw_answer=serializer.validated_data["raw_answer"],
            actor=request.user,
        )
        return Response(
            {
                "answer": InterviewAnswerSerializer(answer).data,
                "generated_facts": ProjectFactSerializer(facts, many=True).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"])
    def answers(self, request, pk=None):
        session = self.get_object()
        queryset = session.answers.select_related("question")
        page = self.paginate_queryset(queryset)
        serializer = InterviewAnswerSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["get"], url_path="next-question")
    def next_question(self, request, pk=None):
        session = self.get_object()
        report = evaluate_completion(session)
        if report["complete"]:
            return Response({"complete": True, "question": None, "coverage": report["criteria"]})
        selection = engine.select_next_question(session)
        if selection is None:
            return Response(
                {
                    "complete": False,
                    "question": None,
                    "coverage": report["criteria"],
                    "message": (
                        "적용 가능한 질문이 더 이상 없습니다. 질문 데이터 보강이 필요합니다."
                    ),
                }
            )
        question, log = selection
        return Response(
            {
                "complete": False,
                "question": QuestionSerializer(question).data,
                "selection": {
                    "total_score": log.total_score,
                    "score_breakdown": log.score_breakdown,
                    "reason": log.reason,
                },
            }
        )

    @action(detail=True, methods=["get"])
    def facts(self, request, pk=None):
        session = self.get_object()
        queryset = fact_selectors.facts_for_project(project_id=session.project_id)
        page = self.paginate_queryset(queryset)
        serializer = ProjectFactSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["get"])
    def state(self, request, pk=None):
        session = self.get_object()
        return Response(
            {
                "project": session.project_id,
                "state": fact_selectors.project_state(project_id=session.project_id),
            }
        )

    @action(detail=True, methods=["get"])
    def progress(self, request, pk=None):
        session = self.get_object()
        report = evaluate_completion(session)
        return Response(
            {
                "status": session.status,
                "answered_count": session.answers.count(),
                "known_fact_count": len(
                    fact_selectors.project_state(project_id=session.project_id)
                ),
                "completion": report,
            }
        )

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        session = services.complete_session(session=self.get_object(), actor=request.user)
        return Response(InterviewSessionSerializer(session).data)
