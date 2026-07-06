import factory

from apps.knowledge.models import KnowledgeItem, KnowledgeType


class KnowledgeItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = KnowledgeItem

    code = factory.Sequence(lambda n: f"KB-{n:04d}")
    knowledge_type = KnowledgeType.SENSOR
    title = "증기 환경 레벨 측정"
