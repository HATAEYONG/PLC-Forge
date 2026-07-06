"""최소 JSONLogic 평가기 (D4).

Question.required_conditions / exclusion_conditions / Rule.conditions_json 이 공유하는
선언형 조건 문법. 지원 연산자:

    {"var": "KEY"}                 — 데이터에서 값 조회 (없으면 None)
    {"==": [a, b]}  {"!=": [a, b]}
    {">": [a, b]}   {">=": [a, b]}  {"<": [a, b]}  {"<=": [a, b]}
    {"and": [...]}  {"or": [...]}   {"!": a}
    {"in": [needle, haystack]}
    {"missing": ["KEY", ...]}      — 없는 키 목록 반환 (빈 목록 = falsy)

빈 dict({})는 "조건 없음"으로 True 취급한다.
"""

from core.exceptions import DomainError


class UnknownOperatorError(DomainError):
    code = "unknown_condition_operator"


def evaluate(logic, data):
    """JSONLogic 표현식을 평가해 truthy 여부를 반환한다."""
    return bool(_apply(logic, data or {}))


def _apply(logic, data):
    if logic is None or logic == {}:
        return True
    if not isinstance(logic, dict):
        return logic

    if len(logic) != 1:
        raise UnknownOperatorError(f"조건식은 연산자 1개를 가져야 합니다: {logic}")
    operator, args = next(iter(logic.items()))

    if operator == "var":
        key = args if isinstance(args, str) else _apply(args, data)
        return data.get(key)
    if operator == "missing":
        keys = args if isinstance(args, list) else [args]
        return [key for key in keys if key not in data]

    if operator == "!":
        return not _apply(args, data)
    if operator == "and":
        result = True
        for arg in args:
            result = _apply(arg, data)
            if not result:
                return result
        return result
    if operator == "or":
        result = False
        for arg in args:
            result = _apply(arg, data)
            if result:
                return result
        return result

    values = [_apply(arg, data) for arg in (args if isinstance(args, list) else [args])]
    if operator == "==":
        return values[0] == values[1]
    if operator == "!=":
        return values[0] != values[1]
    if operator in {">", ">=", "<", "<="}:
        left, right = values[0], values[1]
        if left is None or right is None:
            return False
        if operator == ">":
            return left > right
        if operator == ">=":
            return left >= right
        if operator == "<":
            return left < right
        return left <= right
    if operator == "in":
        needle, haystack = values[0], values[1]
        if haystack is None:
            return False
        return needle in haystack

    raise UnknownOperatorError(f"지원하지 않는 조건 연산자: '{operator}'")
