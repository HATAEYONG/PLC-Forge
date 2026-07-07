"""초기 지식베이스 데이터 (PRD §27 범위).

Industry 5 / Process 10 / Device 10 / Sensor 10.
review_status는 DRAFT로 로드하며, 전문가 검토 후 APPROVED로 승격한다 (PRD §11).
"""


def _item(code, ktype, title, description="", **extra):
    return {
        "code": code,
        "knowledge_type": ktype,
        "title": title,
        "description": description,
        **extra,
    }


KNOWLEDGE_ITEMS = [
    # ── Industry (5) ──
    _item(
        "KB-IND-FOOD", "INDUSTRY", "식품 제조", "위생(CIP/워시다운), 배합, 온도 이력 관리가 핵심."
    ),
    _item("KB-IND-WATER", "INDUSTRY", "수처리", "응집·침전·여과·소독 계통, 약품 주입, 수질 감시."),
    _item("KB-IND-MFG", "INDUSTRY", "일반 제조", "모터/컨베이어 중심 이산 제어와 계량."),
    _item("KB-IND-LOGISTICS", "INDUSTRY", "물류", "반송·분류, 바코드/비전, 저온 환경 가능."),
    _item("KB-IND-SMARTFARM", "INDUSTRY", "스마트팜", "환경(온습도·CO2) 제어와 관수/양액."),
    # ── Process (10) ──
    _item("KB-PROC-TANK", "PROCESS", "탱크 저장", "레벨 감시, 오버플로 보호, 교반 여부 확인."),
    _item("KB-PROC-TRANSFER", "PROCESS", "액체 이송", "펌프 제어, 유량/압력 감시, 드라이런 방지."),
    _item("KB-PROC-MIXING", "PROCESS", "교반/혼합", "교반 속도·시간, 부하 감시."),
    _item("KB-PROC-HEATING", "PROCESS", "가열", "온도 PID, 과열 인터록, 증기/열매 취급."),
    _item("KB-PROC-COOLING", "PROCESS", "냉각", "냉매/냉수 제어, 결로 관리."),
    _item("KB-PROC-CONVEYOR", "PROCESS", "컨베이어 이송", "구간 인터록, 정체·낙하 감지, 비상정지."),
    _item("KB-PROC-PACKAGING", "PROCESS", "포장", "정량 충전, 실링, 검사 연동."),
    _item("KB-PROC-INSPECTION", "PROCESS", "검사", "비전/센서 판정, 불량 배출."),
    _item("KB-PROC-BATCH", "PROCESS", "배치 공정", "레시피 기반 순차 운전, 배치 기록."),
    _item("KB-PROC-CONTINUOUS", "PROCESS", "연속 공정", "정상상태 제어, 연속 데이터 로깅."),
    # ── Device (10) ──
    _item("KB-DEV-MOTOR", "DEVICE", "모터", "기동/정지, 과부하, 상태 피드백."),
    _item("KB-DEV-PUMP", "DEVICE", "펌프", "드라이런 방지, 유량/압력 연동."),
    _item("KB-DEV-VALVE", "DEVICE", "밸브", "개폐 피드백, 페일세이프 위치."),
    _item("KB-DEV-TANK", "DEVICE", "탱크", "레벨/온도 감시, 오버플로 보호."),
    _item("KB-DEV-CYLINDER", "DEVICE", "실린더", "전/후진 감지, 공압 압력 감시."),
    _item("KB-DEV-CONVEYOR", "DEVICE", "컨베이어", "구간 연동, 비상정지, 정체 감지."),
    _item("KB-DEV-HEATER", "DEVICE", "히터", "과열 방지 인터록, 온도 피드백 필수."),
    _item("KB-DEV-FAN", "DEVICE", "팬", "차압 감시, 인터록 연동."),
    _item("KB-DEV-INVERTER", "DEVICE", "인버터", "통신 제어 권장, 고장 코드 수집."),
    _item(
        "KB-DEV-ESTOP",
        "DEVICE",
        "비상정지",
        "안전 회로, 수동 리셋, 이중화 검토.",
        constraints_json=[{"safety": True}],
    ),
    # ── Sensor (10) ──
    _item(
        "KB-SEN-LEVEL-RADAR",
        "SENSOR",
        "레벨 - 레이더",
        "증기·거품·비접촉 환경에 적합. 4-20mA/HART.",
        conditions_json={"and": [{"var": "CONTINUOUS_LEVEL_REQUIRED"}, {"var": "STEAM_PRESENT"}]},
        recommendations_json=[{"principle": "RADAR", "signal": "4-20mA/HART"}],
    ),
    _item("KB-SEN-LEVEL-SWITCH", "SENSOR", "레벨 - 스위치", "상/하한 감지에 적합. DI 신호."),
    _item("KB-SEN-TEMP-RTD", "SENSOR", "온도 - RTD", "정밀 온도, Pt100. AI/통신."),
    _item("KB-SEN-PRESSURE", "SENSOR", "압력", "게이지/차압, 4-20mA."),
    _item("KB-SEN-FLOW-MAG", "SENSOR", "유량 - 전자유량계", "도전성 액체, 비접촉 측정."),
    _item("KB-SEN-PROXIMITY", "SENSOR", "근접", "금속 감지, DI."),
    _item("KB-SEN-PHOTO", "SENSOR", "광전", "물체 유무/위치 감지."),
    _item("KB-SEN-LOADCELL", "SENSOR", "로드셀", "중량 계량, 배합 연동."),
    _item("KB-SEN-CURRENT", "SENSOR", "전류", "모터 부하 감시, CT."),
    _item("KB-SEN-PH", "SENSOR", "pH/수질", "수처리 약품 주입 연동. 세정 주기 관리."),
]
