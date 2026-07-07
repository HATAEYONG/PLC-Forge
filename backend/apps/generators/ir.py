"""Vendor Independent Intermediate Representation (PRD §20).

모든 제조사별 코드 생성기의 공통 입력. 프로젝트 산출물을 벤더 중립 IR로 변환하고
JSON Schema로 검증한다. §20의 연산(ADD~CONTROL_FLOW)을 LogicExpressions로 표현한다.
"""

from jsonschema import Draft202012Validator

from core.exceptions import DomainError

# §20 명시 연산 집합
OPERATIONS = {
    "ADD",
    "SUB",
    "MUL",
    "DIV",
    "COMPARE",
    "MOVE",
    "WORD_OPERATION",
    "BIT_OPERATION",
    "TIMER",
    "COUNTER",
    "SET_RESET",
    "CONTROL_FLOW",
}

# 신호 유형 → 벤더 중립 데이터 타입
SIGNAL_DATA_TYPE = {"DI": "BOOL", "DO": "BOOL", "AI": "REAL", "AO": "REAL"}

IR_SCHEMA = {
    "type": "object",
    "required": [
        "project_metadata",
        "signal_definitions",
        "data_types",
        "logic_expressions",
        "alarms",
        "interlocks",
        "sequences",
        "hmi_tags",
        "test_requirements",
    ],
    "properties": {
        "project_metadata": {
            "type": "object",
            "required": ["code", "name"],
            "properties": {"code": {"type": "string"}, "name": {"type": "string"}},
        },
        "device_definitions": {"type": "array"},
        "signal_definitions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "signal_type", "data_type"],
                "properties": {
                    "name": {"type": "string"},
                    "signal_type": {"enum": ["DI", "DO", "AI", "AO"]},
                    "data_type": {"enum": ["BOOL", "INT", "REAL", "WORD"]},
                },
            },
        },
        "data_types": {"type": "array", "items": {"type": "string"}},
        "logic_expressions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["operation"],
                "properties": {"operation": {"enum": sorted(OPERATIONS)}},
            },
        },
        "alarms": {"type": "array"},
        "interlocks": {"type": "array"},
        "sequences": {"type": "array"},
        "hmi_tags": {"type": "array"},
        "test_requirements": {"type": "array"},
    },
}

_VALIDATOR = Draft202012Validator(IR_SCHEMA)


def _sanitize(name: str) -> str:
    """IEC 61131-3 식별자로 안전하게 변환."""
    safe = "".join(ch if ch.isalnum() else "_" for ch in name)
    if safe and safe[0].isdigit():
        safe = f"T_{safe}"
    return safe or "TAG"


def build_ir(project) -> dict:
    """프로젝트 산출물을 Vendor Independent IR로 변환한다."""
    signals = []
    for point in project.io_points.all():
        signals.append(
            {
                "name": _sanitize(point.tag),
                "signal_type": point.signal_type,
                "data_type": SIGNAL_DATA_TYPE.get(point.signal_type, "BOOL"),
                "description": point.description,
            }
        )

    logic_expressions = []

    # 인터록 → COMPARE + SET_RESET 로직
    interlocks = []
    for il in project.interlocks.all():
        interlocks.append(
            {
                "code": _sanitize(il.code),
                "protected_device": il.protected_device,
                "condition": il.condition,
                "effect": il.effect,
                "safety_related": il.safety_related,
            }
        )
        logic_expressions.append(
            {
                "operation": "SET_RESET",
                "target": _sanitize(il.code),
                "set_condition": il.condition,
                "reset_condition": il.reset_condition or "MANUAL",
                "comment": f"Interlock {il.code}",
            }
        )

    # 알람 → COMPARE 로직
    alarms = []
    for al in project.alarms.all():
        alarms.append(
            {
                "code": _sanitize(al.code),
                "condition": al.condition,
                "priority": al.priority,
                "latching": al.latching,
            }
        )
        logic_expressions.append(
            {
                "operation": "COMPARE",
                "target": _sanitize(al.code),
                "condition": al.condition,
                "comment": f"Alarm {al.code}",
            }
        )

    # 시퀀스 → CONTROL_FLOW
    sequences = []
    for seq in project.sequences.prefetch_related("steps"):
        steps = [
            {
                "step_no": st.step_no,
                "name": st.name,
                "entry_condition": st.entry_condition,
                "completion_condition": st.completion_condition,
                "next_step": st.next_step,
                "timeout_seconds": st.timeout_seconds,
            }
            for st in seq.steps.all()
        ]
        sequences.append({"code": _sanitize(seq.code), "name": seq.name, "steps": steps})
        logic_expressions.append(
            {"operation": "CONTROL_FLOW", "target": _sanitize(seq.code), "steps": len(steps)}
        )

    hmi_tags = []
    for screen in project.hmi_screens.prefetch_related("tags"):
        for tag in screen.tags.all():
            hmi_tags.append({"name": _sanitize(tag.name), "screen": screen.code})

    test_requirements = [
        {"test_id": t.test_id, "phase": t.phase, "category": t.category}
        for t in project.test_cases.all()
    ]

    data_types = sorted({s["data_type"] for s in signals}) or ["BOOL"]

    return {
        "project_metadata": {"code": project.code, "name": project.name},
        "device_definitions": [],
        "signal_definitions": signals,
        "data_types": data_types,
        "logic_expressions": logic_expressions,
        "alarms": alarms,
        "interlocks": interlocks,
        "sequences": sequences,
        "hmi_tags": hmi_tags,
        "test_requirements": test_requirements,
    }


def validate_ir(ir: dict) -> None:
    """IR을 JSON Schema로 검증한다. 실패 시 DomainError."""
    errors = sorted(_VALIDATOR.iter_errors(ir), key=lambda e: list(e.absolute_path))
    if errors:
        raise DomainError(
            "Vendor Independent IR 검증 실패: " + errors[0].message,
            code="invalid_ir",
            details={"path": list(errors[0].absolute_path), "count": len(errors)},
        )
