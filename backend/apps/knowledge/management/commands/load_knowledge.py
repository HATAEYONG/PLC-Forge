from django.core.management.base import BaseCommand
from django.db import transaction

from apps.knowledge.knowledge_seed import KNOWLEDGE_ITEMS
from apps.knowledge.models import KnowledgeItem


class Command(BaseCommand):
    help = "초기 지식베이스 데이터를 로드한다 (code+version 기준 idempotent upsert)."

    @transaction.atomic
    def handle(self, *args, **options):
        created, updated = 0, 0
        for entry in KNOWLEDGE_ITEMS:
            entry = dict(entry)
            code = entry.pop("code")
            version = entry.pop("version", 1)
            _item, was_created = KnowledgeItem.objects.update_or_create(
                code=code, version=version, defaults=entry
            )
            created += was_created
            updated += not was_created
        self.stdout.write(self.style.SUCCESS(f"지식 로드 완료: 생성 {created}건, 갱신 {updated}건"))
