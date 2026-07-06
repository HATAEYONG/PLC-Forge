from rest_framework.routers import DefaultRouter

from apps.knowledge.views import KnowledgeItemViewSet

router = DefaultRouter()
router.register("knowledge-items", KnowledgeItemViewSet)

urlpatterns = router.urls
