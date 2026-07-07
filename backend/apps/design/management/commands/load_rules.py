from django.core.management.base import BaseCommand
from django.db import transaction

from apps.design.effects import normalize_effect
from apps.design.models import Rule
from apps.design.rules_seed import RULES


class Command(BaseCommand):
    help = "초기 규칙 데이터를 로드한다 (code+version 기준 idempotent upsert)."

    @transaction.atomic
    def handle(self, *args, **options):
        created, updated = 0, 0
        for entry in RULES:
            entry = dict(entry)
            code = entry.pop("code")
            version = entry.pop("version", 1)
            # 시드 무결성: 모든 effect가 유효한 유형인지 로드 시 검증한다.
            for effect in entry.get("effects_json", []):
                normalize_effect(effect)
            _rule, was_created = Rule.objects.update_or_create(
                code=code, version=version, defaults=entry
            )
            created += was_created
            updated += not was_created
        self.stdout.write(self.style.SUCCESS(f"규칙 로드 완료: 생성 {created}건, 갱신 {updated}건"))
