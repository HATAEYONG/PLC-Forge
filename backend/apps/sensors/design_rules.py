"""센서 측정 원리 선정 규칙 (PRD §14, Deterministic Core).

측정 항목 + 환경 조건 → 측정 원리/신호/기술을 결정론적으로 선정한다.
LLM 판단이 아닌 명시적 규칙이다 (PRD §3.3). 실제 벤더 모델은 MVP 범위 밖(§26)이며
Vendor Independent 사양까지만 산출한다.
"""

# 측정 항목별 기본 프로파일
BASE_PROFILES = {
    "LEVEL": {
        "principle": "ULTRASONIC",
        "technology": "비접촉 초음파 레벨",
        "signal_type": "AI",
        "accuracy": "±0.25% FS",
        "response_time": "< 1s",
        "communication_requirements": "4-20mA",
        "knowledge_code": "KB-SEN-LEVEL-SWITCH",
    },
    "TEMPERATURE": {
        "principle": "RTD",
        "technology": "Pt100 측온저항체",
        "signal_type": "AI",
        "accuracy": "±0.5℃",
        "response_time": "수 초",
        "communication_requirements": "4-20mA",
        "knowledge_code": "KB-SEN-TEMP-RTD",
    },
    "PRESSURE": {
        "principle": "PIEZORESISTIVE",
        "technology": "압력 트랜스미터",
        "signal_type": "AI",
        "accuracy": "±0.5% FS",
        "response_time": "< 1s",
        "communication_requirements": "4-20mA",
        "knowledge_code": "KB-SEN-PRESSURE",
    },
    "FLOW": {
        "principle": "ELECTROMAGNETIC",
        "technology": "전자유량계",
        "signal_type": "AI",
        "accuracy": "±0.5% rate",
        "response_time": "< 1s",
        "communication_requirements": "4-20mA/펄스",
        "knowledge_code": "KB-SEN-FLOW-MAG",
    },
    "PH": {
        "principle": "GLASS_ELECTRODE",
        "technology": "pH 전극",
        "signal_type": "AI",
        "accuracy": "±0.1 pH",
        "response_time": "수 초",
        "communication_requirements": "4-20mA",
        "knowledge_code": "KB-SEN-PH",
    },
    "WEIGHT": {
        "principle": "STRAIN_GAUGE",
        "technology": "로드셀",
        "signal_type": "AI",
        "accuracy": "±0.1% FS",
        "response_time": "< 0.5s",
        "communication_requirements": "아날로그/통신",
        "knowledge_code": "KB-SEN-LOADCELL",
    },
    "POSITION": {
        "principle": "INDUCTIVE",
        "technology": "근접 센서",
        "signal_type": "DI",
        "accuracy": "-",
        "response_time": "< 10ms",
        "communication_requirements": "DI",
        "knowledge_code": "KB-SEN-PROXIMITY",
    },
    "VIBRATION": {
        "principle": "PIEZOELECTRIC",
        "technology": "진동 센서",
        "signal_type": "AI",
        "accuracy": "-",
        "response_time": "-",
        "communication_requirements": "4-20mA/통신",
        "knowledge_code": None,
    },
    "CURRENT": {
        "principle": "CT",
        "technology": "변류기",
        "signal_type": "AI",
        "accuracy": "±1%",
        "response_time": "-",
        "communication_requirements": "4-20mA",
        "knowledge_code": "KB-SEN-CURRENT",
    },
}


def select_sensor_profile(measurement_type: str, state: dict) -> dict:
    """측정 항목 + 프로젝트 상태(Fact) → 센서 프로파일. 환경 조건에 따라 원리를 조정한다."""
    profile = dict(
        BASE_PROFILES.get(
            measurement_type,
            {
                "principle": "",
                "technology": "",
                "signal_type": "AI",
                "accuracy": "",
                "response_time": "",
                "communication_requirements": "",
                "knowledge_code": None,
            },
        )
    )

    steam = state.get("STEAM_PRESENT_DURING_CIP") or state.get("STEAM_PRESENT")
    continuous_level = state.get("CONTINUOUS_LEVEL_REQUIRED")

    reasons = []
    if measurement_type == "LEVEL":
        if continuous_level and steam:
            # PRD §14 예: 증기 존재 → 비접촉 레이더
            profile.update(
                principle="RADAR",
                technology="비접촉 레이더 레벨",
                signal_type="AI",
                communication_requirements="4-20mA/HART",
                knowledge_code="KB-SEN-LEVEL-RADAR",
            )
            reasons.append("증기 환경 연속 측정 → 비접촉 레이더")
        elif not continuous_level:
            profile.update(
                principle="FLOAT_SWITCH",
                technology="레벨 스위치",
                signal_type="DI",
                communication_requirements="DI",
                knowledge_code="KB-SEN-LEVEL-SWITCH",
            )
            reasons.append("상/하한 감지 → 레벨 스위치(DI)")

    # 환경/재질 반영
    if state.get("CORROSIVE_MATERIAL"):
        profile["material_compatibility"] = "내부식 재질(예: SUS316L/PTFE) 필요"
        reasons.append("부식성 물질 → 내부식 재질")
    if state.get("SANITARY_REQUIRED"):
        profile["material_compatibility"] = "위생 등급(3-A/EHEDG), 위생 접속"
        reasons.append("위생 요구 → 위생 등급 접속")
    if state.get("CIP_REQUIRED"):
        profile["environmental_rating"] = "IP69K (워시다운/CIP)"
        reasons.append("CIP/워시다운 → IP69K")
    else:
        profile.setdefault("environmental_rating", "IP65")

    profile["is_continuous"] = profile.get("signal_type") == "AI"
    profile["selection_reasons"] = reasons
    return profile
