from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.interview import services
from apps.interview.models import AnswerOption, InterviewSession, Question
from apps.interview.serializers import (
    AnswerOptionSerializer,
    AnswerSubmitSerializer,
    InterviewAnswerSerializer,
    InterviewSessionSerializer,
    QuestionSerializer,
)


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
        answer = services.submit_answer(
            session=session,
            question=serializer.validated_data["question"],
            raw_answer=serializer.validated_data["raw_answer"],
            actor=request.user,
        )
        return Response(InterviewAnswerSerializer(answer).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def answers(self, request, pk=None):
        session = self.get_object()
        queryset = session.answers.select_related("question")
        page = self.paginate_queryset(queryset)
        serializer = InterviewAnswerSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
