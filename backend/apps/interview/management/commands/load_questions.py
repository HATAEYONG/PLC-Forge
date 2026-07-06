from django.core.management.base import BaseCommand
from django.db import transaction
from jsonschema import Draft202012Validator

from apps.interview.models import AnswerOption, Question
from apps.interview.questions_seed import DEFAULT_SCHEMAS, QUESTIONS


class Command(BaseCommand):
    help = "초기 질문 데이터를 로드한다 (code+version 기준 idempotent upsert)."

    @transaction.atomic
    def handle(self, *args, **options):
        created, updated = 0, 0
        for entry in QUESTIONS:
            entry = dict(entry)
            options_data = entry.pop("options", None)
            code = entry.pop("code")
            version = entry.pop("version", 1)
            entry.setdefault("answer_schema", DEFAULT_SCHEMAS[entry["question_type"]])
            Draft202012Validator.check_schema(entry["answer_schema"])

            question, was_created = Question.objects.update_or_create(
                code=code, version=version, defaults=entry
            )
            created += was_created
            updated += not was_created

            if options_data:
                question.options.all().delete()
                AnswerOption.objects.bulk_create(
                    AnswerOption(question=question, value=value, label=label, order=index)
                    for index, (value, label) in enumerate(options_data)
                )

        self.stdout.write(self.style.SUCCESS(f"질문 로드 완료: 생성 {created}건, 갱신 {updated}건"))
