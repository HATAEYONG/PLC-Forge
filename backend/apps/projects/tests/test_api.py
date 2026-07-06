import pytest

from apps.companies.tests.factories import CompanyFactory


@pytest.mark.django_db
def test_project_crud(api_client, user):
    company = CompanyFactory()
    created = api_client.post(
        "/api/projects/",
        {"company": str(company.id), "name": "탱크 자동화", "code": "PRJ-0001"},
        format="json",
    )
    assert created.status_code == 201
    body = created.json()
    assert body["status"] == "DRAFT"
    assert body["created_by"] == str(user.id)

    listed = api_client.get("/api/projects/")
    assert listed.json()["count"] == 1

    patched = api_client.patch(
        f"/api/projects/{body['id']}/", {"status": "INTERVIEWING"}, format="json"
    )
    assert patched.status_code == 200
    assert patched.json()["status"] == "INTERVIEWING"


@pytest.mark.django_db
def test_project_duplicate_code_rejected(api_client):
    company = CompanyFactory()
    payload = {"company": str(company.id), "name": "A", "code": "PRJ-DUP"}
    assert api_client.post("/api/projects/", payload, format="json").status_code == 201
    response = api_client.post("/api/projects/", payload, format="json")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "validation_error"
