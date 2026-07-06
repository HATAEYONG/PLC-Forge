import uuid

from django.db import models


class BaseModel(models.Model):
    """모든 도메인 모델의 공통 베이스: UUID PK + 생성/수정 시각."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class KeyValueEntry(BaseModel):
    """Phase 0 부트스트랩 검증용 — DB 연결 및 한글 UTF-8 왕복 확인에 사용한다."""

    key = models.CharField(max_length=255, unique=True)
    value = models.JSONField(default=dict)

    class Meta:
        db_table = "core_key_value_entry"

    def __str__(self):
        return self.key
