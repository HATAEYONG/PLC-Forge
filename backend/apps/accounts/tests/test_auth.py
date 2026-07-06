import pytest

from apps.accounts.tests.factories import DEFAULT_PASSWORD, UserFactory


@pytest.mark.django_db
def test_jwt_token_obtain_and_me(anon_client):
    user = UserFactory()
    response = anon_client.post(
        "/api/auth/token/",
        {"username": user.username, "password": DEFAULT_PASSWORD},
        format="json",
    )
    assert response.status_code == 200
    tokens = response.json()
    assert "access" in tokens and "refresh" in tokens

    anon_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    me = anon_client.get("/api/auth/me/")
    assert me.status_code == 200
    assert me.json()["username"] == user.username


@pytest.mark.django_db
def test_jwt_wrong_password_returns_error_envelope(anon_client):
    user = UserFactory()
    response = anon_client.post(
        "/api/auth/token/",
        {"username": user.username, "password": "wrong-password"},
        format="json",
    )
    assert response.status_code == 401
    body = response.json()
    assert set(body["error"].keys()) == {"code", "message", "details"}


@pytest.mark.django_db
def test_unauthenticated_request_returns_401_envelope(anon_client):
    response = anon_client.get("/api/companies/")
    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "not_authenticated"
