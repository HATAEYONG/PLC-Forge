"""초기 규칙 데이터 (PRD §12 예시 포함).

⚠️ Safety 관련 효과(REQUIRE_ALARM / REQUIRE_INTERLOCK / REVIEW)를 포함한 규칙은
자동화 전문가 검토 후 확정한다 (D6, PRD §33-15).
"""

RULES = [
    {
        # PRD §12 예시 규칙
        "code": "RULE-LEVEL-RADAR-STEAM",
        "rule_type": "HARD",
        "priority": 100,
        "conditions_json": {
            "and": [
                {">": [{"var": "TANK_COUNT"}, 0]},
                {"==": [{"var": "CONTINUOUS_LEVEL_REQUIRED"}, True]},
                {
                    "or": [
                        {"==": [{"var": "STEAM_PRESENT_DURING_CIP"}, True]},
                        {"==": [{"var": "STEAM_PRESENT"}, True]},
                    ]
                },
            ]
        },
        "effects_json": [
            {
                "effect": "RECOMMEND",
                "subject_type": "SENSOR_PRINCIPLE",
                "subject_id": "LEVEL",
                "value": {"principle": "RADAR", "reason": "증기 환경 비접촉 연속 측정"},
                "risk_level": "MEDIUM",
            },
            {
                "effect": "REQUIRE",
                "subject_type": "IO_SIGNAL",
                "subject_id": "LEVEL",
                "value": {"signal": "AI", "range": "4-20mA/HART"},
            },
            {
                "effect": "REQUIRE_ALARM",
                "subject_type": "ALARM",
                "subject_id": "LEVEL_HIGH",
                "value": {"type": "HIGH_LEVEL", "priority": "HIGH"},
            },
            {
                "effect": "REQUIRE_ALARM",
                "subject_type": "ALARM",
                "subject_id": "LEVEL_LOW",
                "value": {"type": "LOW_LEVEL", "priority": "HIGH"},
            },
            {
                "effect": "REVIEW",
                "subject_type": "PROTECTION",
                "subject_id": "OVERFLOW",
                "value": {"item": "Overflow Protection Review"},
            },
            {
                "effect": "REQUIRE",
                "subject_type": "HMI_OBJECT",
                "subject_id": "LEVEL_TREND",
                "value": {"object": "TREND", "tag": "LEVEL"},
            },
            {
                "effect": "GENERATE_TEST",
                "subject_type": "FAT",
                "subject_id": "LEVEL_SIM",
                "value": {"phase": "FAT", "name": "레벨 센서 시뮬레이션 시험"},
            },
            {
                "effect": "GENERATE_TEST",
                "subject_type": "SAT",
                "subject_id": "LEVEL_VERIFY",
                "value": {"phase": "SAT", "name": "실제 레벨 검증 시험"},
            },
        ],
        "explanation_template": (
            "탱크에 증기가 존재하고 연속 레벨 측정이 필요하므로, 비접촉 레이더 방식을 "
            "권장하고 관련 I/O·알람·보호검토·트렌드·시험을 요구합니다."
        ),
        "severity": "WARNING",
        "applicable_scope": {"knowledge_codes": ["KB-SEN-LEVEL-RADAR"]},
    },
    {
        "code": "RULE-ESTOP-SAFETY-IO",
        "rule_type": "HARD",
        "priority": 90,
        "conditions_json": {"==": [{"var": "ESTOP_REQUIRED"}, True]},
        "effects_json": [
            {
                "effect": "REQUIRE",
                "subject_type": "SAFETY_IO",
                "subject_id": "ESTOP",
                "value": {"signal": "DI", "category": "SAFETY"},
            },
            {
                "effect": "REQUIRE_INTERLOCK",
                "subject_type": "INTERLOCK",
                "subject_id": "ESTOP_TRIP",
                "value": {"effect": "STOP_ALL_ACTUATORS", "reset": "MANUAL"},
            },
        ],
        "explanation_template": "비상정지가 요구되므로 안전 입력과 정지 인터록을 요구합니다.",
        "severity": "CRITICAL",
    },
    {
        "code": "RULE-INVERTER-COMM",
        "rule_type": "RECOMMENDATION",
        "priority": 50,
        "conditions_json": {"==": [{"var": "INVERTER_USED"}, True]},
        "effects_json": [
            {
                "effect": "RECOMMEND",
                "subject_type": "COMMUNICATION",
                "subject_id": "INVERTER",
                "value": {"method": "FIELDBUS", "note": "인버터 통신 제어 권장"},
            },
        ],
        "explanation_template": "인버터 사용 시 개별 배선보다 필드버스 통신 제어를 권장합니다.",
        "severity": "INFO",
    },
]
