"""API 오류 응답 형식 통일 검증 (PRD §33-19).

모든 오류는 {"error": {"code", "message", "details"}} 형식이어야 한다.
"""

import pytest
from rest_framework.test import APIClient


def assert_error_envelope(body):
    assert set(body.keys()) == {"error"}
    assert set(body["error"].keys()) == {"code", "message", "details"}


@pytest.mark.django_db
def test_not_found_uses_error_envelope():
    client = APIClient()
    response = client.get("/api/kv/does-not-exist/")
    assert response.status_code == 404
    body = response.json()
    assert_error_envelope(body)
    assert body["error"]["code"] == "not_found"


@pytest.mark.django_db
def test_validation_error_uses_error_envelope():
    client = APIClient()
    response = client.put("/api/kv/some-key/", data={}, format="json")
    assert response.status_code == 400
    body = response.json()
    assert_error_envelope(body)
    assert body["error"]["code"] == "validation_error"
    assert "value" in body["error"]["details"]


@pytest.mark.django_db
def test_method_not_allowed_uses_error_envelope():
    client = APIClient()
    response = client.post("/api/health/", data={}, format="json")
    assert response.status_code == 405
    body = response.json()
    assert_error_envelope(body)
    assert body["error"]["code"] == "method_not_allowed"
