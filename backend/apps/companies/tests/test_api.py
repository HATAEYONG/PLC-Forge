import pytest

from apps.companies.tests.factories import CompanyFactory


@pytest.mark.django_db
def test_company_crud(api_client):
    created = api_client.post(
        "/api/companies/",
        {"name": "한빛식품", "industry": "식품", "contact_name": "김담당"},
        format="json",
    )
    assert created.status_code == 201
    company_id = created.json()["id"]

    listed = api_client.get("/api/companies/")
    assert listed.status_code == 200
    assert listed.json()["count"] == 1

    detail = api_client.get(f"/api/companies/{company_id}/")
    assert detail.status_code == 200
    assert detail.json()["name"] == "한빛식품"

    patched = api_client.patch(
        f"/api/companies/{company_id}/", {"memo": "탱크 3기 보유"}, format="json"
    )
    assert patched.status_code == 200
    assert patched.json()["memo"] == "탱크 3기 보유"


@pytest.mark.django_db
def test_company_duplicate_name_rejected(api_client):
    CompanyFactory(name="중복상사")
    response = api_client.post("/api/companies/", {"name": "중복상사"}, format="json")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "validation_error"
