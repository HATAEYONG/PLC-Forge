"""단위 정규화 (PRD §9 Unit Conversion 단계, D8: SI 저장 + 원본 단위 보존).

MVP는 온도만 정식 변환하고, 그 외 단위는 표기 정규화만 수행한다.
확장 시 pint 도입을 검토한다 (DECISIONS_REQUIRED.md D8).
"""

TEMPERATURE_ALIASES = {"도", "℃", "°C", "C", "c", "celsius"}
FAHRENHEIT_ALIASES = {"℉", "°F", "F", "fahrenheit"}


def normalize_unit_value(value, unit):
    """(값, 단위)를 표준 표기로 정규화한다. 반환: (값, 표준단위, 원본단위)."""
    unit = (unit or "").strip()
    if unit in TEMPERATURE_ALIASES:
        return value, "C", unit
    if unit in FAHRENHEIT_ALIASES:
        return round((value - 32) * 5 / 9, 2), "C", unit
    return value, unit, unit
