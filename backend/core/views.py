from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import KeyValueEntry


class HealthView(APIView):
    """DB 연결을 포함한 서비스 상태 확인."""

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        db_ok = True
        try:
            with connections["default"].cursor() as cursor:
                cursor.execute("SELECT 1")
        except OperationalError:
            db_ok = False
        return Response(
            {
                "status": "ok" if db_ok else "degraded",
                "db": db_ok,
                "version": settings.VERSION,
            },
            status=status.HTTP_200_OK if db_ok else status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class KeyValueView(APIView):
    """Phase 0 부트스트랩 검증용 Key-Value API (UTF-8 왕복 확인)."""

    authentication_classes = []
    permission_classes = []

    def get(self, request, key):
        entry = get_object_or_404(KeyValueEntry, key=key)
        return Response({"key": entry.key, "value": entry.value})

    def put(self, request, key):
        if not isinstance(request.data, dict) or "value" not in request.data:
            raise ValidationError({"value": ["이 필드는 필수입니다."]})
        entry, _created = KeyValueEntry.objects.update_or_create(
            key=key, defaults={"value": request.data["value"]}
        )
        return Response({"key": entry.key, "value": entry.value})
