import factory

from apps.interview.models import InterviewSession, Question, QuestionCategory, QuestionType
from apps.projects.tests.factories import ProjectFactory


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question

    code = factory.Sequence(lambda n: f"Q-{n:04d}")
    text = "탱크는 몇 개입니까?"
    category = QuestionCategory.DEVICE
    question_type = QuestionType.INTEGER


class InterviewSessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InterviewSession

    project = factory.SubFactory(ProjectFactory)
