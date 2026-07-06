import pytest

from core.jsonlogic import UnknownOperatorError, evaluate

DATA = {"TANK_COUNT": 3, "STEAM_PRESENT": True, "INDUSTRY": "식품", "MAX_TEMP": 80}


def test_empty_condition_is_true():
    assert evaluate({}, DATA) is True
    assert evaluate(None, DATA) is True


def test_var_and_equality():
    assert evaluate({"==": [{"var": "TANK_COUNT"}, 3]}, DATA)
    assert not evaluate({"==": [{"var": "TANK_COUNT"}, 4]}, DATA)
    assert evaluate({"!=": [{"var": "INDUSTRY"}, "수처리"]}, DATA)


def test_comparisons():
    assert evaluate({">": [{"var": "MAX_TEMP"}, 60]}, DATA)
    assert evaluate({"<=": [{"var": "TANK_COUNT"}, 3]}, DATA)
    assert not evaluate({">": [{"var": "MISSING_KEY"}, 1]}, DATA)


def test_boolean_operators():
    assert evaluate({"and": [{"var": "STEAM_PRESENT"}, {">": [{"var": "TANK_COUNT"}, 1]}]}, DATA)
    assert evaluate({"or": [{"var": "NOPE"}, {"var": "STEAM_PRESENT"}]}, DATA)
    assert evaluate({"!": {"var": "NOPE"}}, DATA)


def test_in_and_missing():
    assert evaluate({"in": [{"var": "INDUSTRY"}, ["식품", "수처리"]]}, DATA)
    assert evaluate({"missing": ["NOPE"]}, DATA) is True  # 누락 키 존재 → truthy
    assert evaluate({"missing": ["TANK_COUNT"]}, DATA) is False


def test_unknown_operator_raises():
    with pytest.raises(UnknownOperatorError):
        evaluate({"regex": ["a", "b"]}, DATA)
