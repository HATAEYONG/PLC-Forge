import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_health_returns_ok_with_db_connected():
    client = APIClient()
    response = client.get("/api/health/")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["db"] is True
    assert body["version"]
