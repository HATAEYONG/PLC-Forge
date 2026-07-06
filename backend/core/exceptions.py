"""API 오류 응답 형식 통일 (PRD §33-19).

모든 API 오류는 다음 형식으로 반환한다:

    {"error": {"code": str, "message": str, "details": object | null}}
"""

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


class DomainError(Exception):
    """Service Layer의 도메인 규칙 위반. 통일 오류 포맷으로 매핑된다."""

    code = "domain_error"
    status_code = 400

    def __init__(self, message, *, code=None, status_code=None, details=None):
        super().__init__(message)
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code
        self.details = details


def exception_handler(exc, context):
    if isinstance(exc, DomainError):
        return Response(
            {"error": {"code": exc.code, "message": str(exc), "details": exc.details}},
            status=exc.status_code,
        )

    # DRF 기본 핸들러와 동일한 예외 변환을 적용해 code 매핑을 일관되게 유지한다.
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    response = drf_exception_handler(exc, context)
    if response is None:
        # DRF가 처리하지 못한 예외는 Django 기본 500 처리에 맡긴다.
        return None

    if isinstance(exc, exceptions.ValidationError):
        code = "validation_error"
        message = "입력값이 올바르지 않습니다."
        details = response.data
    elif isinstance(exc, exceptions.APIException):
        code = getattr(exc, "default_code", "error")
        message = str(exc.detail)
        details = None
    else:
        code = "error"
        message = str(exc)
        details = None

    response.data = {"error": {"code": code, "message": message, "details": details}}
    return response
