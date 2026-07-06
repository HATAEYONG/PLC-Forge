"""한글 UTF-8 저장/조회 왕복 테스트 (PRD §33-20)."""

import pytest
from rest_framework.test import APIClient

from core.models import KeyValueEntry

KOREAN_SAMPLE = "탱크가 3개 있고 그중 두 개는 80℃ 정도이며 세척할 때 증기가 생깁니다."


@pytest.mark.django_db
def test_korean_text_roundtrip_through_orm():
    KeyValueEntry.objects.create(key="현장답변", value={"원문": KOREAN_SAMPLE, "온도": "80℃"})
    entry = KeyValueEntry.objects.get(key="현장답변")
    assert entry.value["원문"] == KOREAN_SAMPLE
    assert entry.value["원문"].encode("utf-8") == KOREAN_SAMPLE.encode("utf-8")
    assert entry.value["온도"] == "80℃"


@pytest.mark.django_db
def test_korean_text_roundtrip_through_api():
    client = APIClient()
    put_response = client.put(
        "/api/kv/인터뷰-답변-1/",
        data={"value": {"원문": KOREAN_SAMPLE}},
        format="json",
    )
    assert put_response.status_code == 200

    get_response = client.get("/api/kv/인터뷰-답변-1/")
    assert get_response.status_code == 200
    assert get_response.json()["value"]["원문"] == KOREAN_SAMPLE
