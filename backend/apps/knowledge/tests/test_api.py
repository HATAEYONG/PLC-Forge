import pytest


@pytest.mark.django_db
def test_knowledge_item_crud(api_client):
    created = api_client.post(
        "/api/knowledge-items/",
        {
            "code": "KB-LEVEL-STEAM",
            "knowledge_type": "SENSOR",
            "title": "증기 환경에서는 레이더 레벨 측정을 우선한다",
            "description": "증기·응축이 있는 탱크에서 초음파는 오차가 크다.",
            "conditions_json": {"and": [{"var": "STEAM_PRESENT"}, {"var": "TANK_EXISTS"}]},
            "recommendations_json": [{"principle": "RADAR", "signal": "4-20mA/HART"}],
        },
        format="json",
    )
    assert created.status_code == 201
    item_id = created.json()["id"]
    assert created.json()["review_status"] == "DRAFT"

    listed = api_client.get("/api/knowledge-items/")
    assert listed.json()["count"] == 1

    patched = api_client.patch(
        f"/api/knowledge-items/{item_id}/", {"review_status": "APPROVED"}, format="json"
    )
    assert patched.status_code == 200
    assert patched.json()["review_status"] == "APPROVED"
