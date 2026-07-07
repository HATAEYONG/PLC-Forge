import pytest
from django.core.management import call_command

from apps.knowledge.knowledge_seed import KNOWLEDGE_ITEMS
from apps.knowledge.models import KnowledgeItem, KnowledgeType


@pytest.mark.django_db
def test_load_knowledge_is_idempotent_and_covers_scope():
    call_command("load_knowledge")
    assert KnowledgeItem.objects.count() == len(KNOWLEDGE_ITEMS)
    call_command("load_knowledge")
    assert KnowledgeItem.objects.count() == len(KNOWLEDGE_ITEMS)

    # PRD §27 범위: Industry 5, Process 10, Device 10, Sensor 10
    assert KnowledgeItem.objects.filter(knowledge_type=KnowledgeType.INDUSTRY).count() == 5
    assert KnowledgeItem.objects.filter(knowledge_type=KnowledgeType.PROCESS).count() == 10
    assert KnowledgeItem.objects.filter(knowledge_type=KnowledgeType.DEVICE).count() == 10
    assert KnowledgeItem.objects.filter(knowledge_type=KnowledgeType.SENSOR).count() == 10


@pytest.mark.django_db
def test_seed_codes_unique():
    codes = [item["code"] for item in KNOWLEDGE_ITEMS]
    assert len(codes) == len(set(codes))
