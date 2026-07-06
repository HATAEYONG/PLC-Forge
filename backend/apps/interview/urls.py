from rest_framework.routers import DefaultRouter

from apps.interview.views import AnswerOptionViewSet, InterviewSessionViewSet, QuestionViewSet

router = DefaultRouter()
router.register("questions", QuestionViewSet)
router.register("answer-options", AnswerOptionViewSet)
router.register("interview/sessions", InterviewSessionViewSet, basename="interview-session")

urlpatterns = router.urls
