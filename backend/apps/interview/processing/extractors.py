"""한국어 자연어 답변의 Rule-based Entity Extraction (PRD §9).

LLM 없이 동작하는 결정론적 추출기 (PRD §33-13). LLM 도입 시 이 모듈과 동일한
FactDraft 인터페이스를 구현하는 LLM Extractor를 추가한다 (PRD §33-12).
추출 결과는 confidence < 1.0의 PROPOSED Fact가 되며, 사용자 확인 후 CONFIRMED 된다.
"""

import re
from dataclasses import dataclass

from apps.requirements.models import ValueType

from .units import normalize_unit_value

TEXT_EXTRACTION_CONFIDENCE = 0.7

KOREAN_COUNT_WORDS = {"한": 1, "두": 2, "세": 3, "네": 4, "다섯": 5}
_COUNT_WORD_PATTERN = "|".join(KOREAN_COUNT_WORDS)


@dataclass
class FactDraft:
    fact_key: str
    value: object
    value_type: str
    unit: str = ""
    confidence: float = TEXT_EXTRACTION_CONFIDENCE


def _to_count(token: str) -> int:
    return KOREAN_COUNT_WORDS.get(token) or int(token)


def extract_tank_count(text):
    match = re.search(r"탱크\s*(?:가|는|를|도)?\s*(\d+|" + _COUNT_WORD_PATTERN + r")\s*개", text)
    if match:
        yield FactDraft("TANK_COUNT", _to_count(match.group(1)), ValueType.NUMBER)


def extract_heated_tanks_and_temperature(text):
    match = re.search(
        r"(?:그\s*중|그중|이\s*중|중)\s*(\d+|"
        + _COUNT_WORD_PATTERN
        + r")\s*개?(?:는|가|만)?[^.।]*?(\d+(?:\.\d+)?)\s*(도|℃|°C|℉|°F)",
        text,
    )
    if match:
        count = _to_count(match.group(1))
        value, unit, _original = normalize_unit_value(float(match.group(2)), match.group(3))
        yield FactDraft("HEATED_TANK_COUNT", count, ValueType.NUMBER)
        yield FactDraft("MAX_TEMPERATURE_APPROX", value, ValueType.NUMBER, unit=unit)
        return
    # 온도만 단독 언급된 경우
    match = re.search(r"(\d+(?:\.\d+)?)\s*(도|℃|°C|℉|°F)", text)
    if match:
        value, unit, _original = normalize_unit_value(float(match.group(1)), match.group(2))
        yield FactDraft("MAX_TEMPERATURE_APPROX", value, ValueType.NUMBER, unit=unit)


def extract_cip_and_steam(text):
    cip_mentioned = ("세척" in text) or ("CIP" in text.upper())
    if cip_mentioned:
        yield FactDraft("CIP_REQUIRED", True, ValueType.BOOLEAN)
        if "증기" in text:
            yield FactDraft("STEAM_PRESENT_DURING_CIP", True, ValueType.BOOLEAN)
    elif "증기" in text:
        yield FactDraft("STEAM_PRESENT", True, ValueType.BOOLEAN)


TEXT_EXTRACTORS = [
    extract_tank_count,
    extract_heated_tanks_and_temperature,
    extract_cip_and_steam,
]


def extract_facts_from_text(text: str) -> list[FactDraft]:
    drafts = []
    for extractor in TEXT_EXTRACTORS:
        drafts.extend(extractor(text))
    return drafts
