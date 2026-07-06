import pytest


@pytest.mark.django_db
def test_rule_crud(api_client):
    created = api_client.post(
        "/api/rules/",
        {
            "code": "RULE-RADAR-LEVEL",
            "rule_type": "HARD",
            "priority": 100,
            "conditions_json": {
                "and": [
                    {"var": "TANK_EXISTS"},
                    {"var": "LIQUID_PROCESS"},
                    {"var": "CONTINUOUS_LEVEL_REQUIRED"},
                    {"var": "STEAM_PRESENT"},
                ]
            },
            "effects_json": [
                {"recommend_measurement_principle": "RADAR"},
                {"require_io": "AI"},
                {"require_alarm": "HIGH_LEVEL"},
                {"require_alarm": "LOW_LEVEL"},
            ],
            "explanation_template": "증기 환경 탱크 연속 레벨 측정에는 레이더 방식을 권장합니다.",
            "severity": "WARNING",
        },
        format="json",
    )
    assert created.status_code == 201
    rule_id = created.json()["id"]
    assert created.json()["rule_type"] == "HARD"

    patched = api_client.patch(f"/api/rules/{rule_id}/", {"is_active": False}, format="json")
    assert patched.status_code == 200
    assert patched.json()["is_active"] is False
