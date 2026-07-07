"""HMI Design Engine (PRD §17).

질문 답변과 설계 상태에 따라 필요한 화면만 생성한다. 각 화면은 목적/역할/보안등급과
Required Tags·Commands·Status·Alarm·Trend·Navigation을 가진다.
"""

from django.db import transaction

from apps.design.models import RiskLevel
from apps.design.services import create_design_decision
from apps.hmi_design.models import HMIScreen, HMITag, SecurityLevel
from apps.requirements.models import ProjectFact
from apps.requirements.selectors import project_state
from apps.requirements.services import ACTIVE_STATUSES

# 기본 화면 세트 (HMI가 필요하면 항상 생성)
BASE_SCREENS = [
    {
        "code": "MAIN_OVERVIEW",
        "name": "메인 개요",
        "purpose": "전체 공정 상태 요약",
        "security_level": SecurityLevel.OPERATOR,
    },
    {
        "code": "PROCESS_OVERVIEW",
        "name": "공정 개요",
        "purpose": "공정 흐름 감시",
        "security_level": SecurityLevel.OPERATOR,
    },
    {
        "code": "MANUAL_OPERATION",
        "name": "수동 운전",
        "purpose": "설비 개별 수동 조작",
        "security_level": SecurityLevel.OPERATOR,
    },
    {
        "code": "ALARM_SUMMARY",
        "name": "알람 요약",
        "purpose": "현재 알람 목록",
        "security_level": SecurityLevel.OPERATOR,
    },
    {
        "code": "ALARM_HISTORY",
        "name": "알람 이력",
        "purpose": "알람 발생/복귀 이력",
        "security_level": SecurityLevel.SUPERVISOR,
    },
    {
        "code": "SYSTEM_SETTINGS",
        "name": "시스템 설정",
        "purpose": "통신/시각 등 설정",
        "security_level": SecurityLevel.ENGINEER,
    },
    {
        "code": "USER_MANAGEMENT",
        "name": "사용자 관리",
        "purpose": "권한 관리",
        "security_level": SecurityLevel.SUPERVISOR,
    },
]


# 조건부 화면: (fact_key/조건 함수, 화면 정의)
def _conditional_screens(flat, has_io, has_interlock):
    screens = []
    if flat.get("CONTROL_MODE") in ("AUTO", "SEMI"):
        screens.append(
            {
                "code": "AUTO_SEQUENCE",
                "name": "자동 시퀀스",
                "purpose": "자동 운전 순서 감시/제어",
                "security_level": SecurityLevel.OPERATOR,
            }
        )
    if flat.get("TREND_REQUIRED"):
        screens.append(
            {
                "code": "TREND",
                "name": "트렌드",
                "purpose": "측정값 추이 그래프",
                "security_level": SecurityLevel.OPERATOR,
            }
        )
    if flat.get("RECIPE_REQUIRED"):
        screens.append(
            {
                "code": "RECIPE",
                "name": "레시피",
                "purpose": "배합/운전 조건 관리",
                "security_level": SecurityLevel.SUPERVISOR,
            }
        )
    if has_io:
        screens.append(
            {
                "code": "IO_MONITOR",
                "name": "I/O 모니터",
                "purpose": "입출력 상태 감시",
                "security_level": SecurityLevel.ENGINEER,
            }
        )
    if has_interlock or flat.get("ESTOP_REQUIRED") or flat.get("INTERLOCK_REQUIREMENTS"):
        screens.append(
            {
                "code": "INTERLOCK_STATUS",
                "name": "인터록 상태",
                "purpose": "인터록/바이패스 상태",
                "security_level": SecurityLevel.SUPERVISOR,
            }
        )
    if flat.get("SCADA_REQUIRED") or flat.get("MES_INTEGRATION_REQUIRED"):
        screens.append(
            {
                "code": "COMM_STATUS",
                "name": "통신 상태",
                "purpose": "네트워크 노드 상태",
                "security_level": SecurityLevel.ENGINEER,
            }
        )
    if flat.get("QUALITY_LOGGING_REQUIRED") or flat.get("HISTORIAN_REQUIRED"):
        screens.append(
            {
                "code": "REPORT",
                "name": "리포트",
                "purpose": "생산/품질 보고서",
                "security_level": SecurityLevel.SUPERVISOR,
            }
        )
    if flat.get("MAINTENANCE_CAPABILITY"):
        screens.append(
            {
                "code": "MAINTENANCE",
                "name": "유지보수",
                "purpose": "정비 정보/카운터",
                "security_level": SecurityLevel.ENGINEER,
            }
        )
    return screens


def _flat_state(project):
    state = project_state(project_id=project.id)
    return {key: info["value"] for key, info in state.items()}


@transaction.atomic
def generate_hmi(*, project, actor=None):
    """설계 상태 조건에 따라 필요한 HMI 화면만 생성한다 (idempotent)."""
    project.hmi_screens.all().delete()

    flat = _flat_state(project)
    if not flat.get("HMI_REQUIRED"):
        return {"screens": 0, "skipped": "HMI 불필요"}

    io_points = list(project.io_points.all())
    has_io = bool(io_points)
    has_interlock = project.design_decisions.filter(decision_type="INTERLOCK_REQUIREMENT").exists()

    facts = list(
        ProjectFact.objects.filter(
            project=project,
            fact_key__in=[
                "HMI_REQUIRED",
                "CONTROL_MODE",
                "TREND_REQUIRED",
                "RECIPE_REQUIRED",
                "SCADA_REQUIRED",
                "ESTOP_REQUIRED",
            ],
            status__in=ACTIVE_STATUSES,
        )
    )
    decision = create_design_decision(
        project=project,
        decision_type="HMI_DESIGN",
        subject_type="HMI",
        decision_value={"summary": "HMI 화면 구조"},
        reason="설계 상태 조건에 따라 필요한 화면만 생성",
        input_facts=facts,
        risk_level=RiskLevel.LOW,
        actor=actor,
    )

    all_screens = BASE_SCREENS + _conditional_screens(flat, has_io, has_interlock)
    created = []
    for order, spec in enumerate(all_screens):
        screen = HMIScreen.objects.create(
            project=project,
            decision=decision,
            code=spec["code"],
            name=spec["name"],
            purpose=spec.get("purpose", ""),
            user_role=spec.get("security_level", SecurityLevel.OPERATOR),
            security_level=spec.get("security_level", SecurityLevel.OPERATOR),
            order=order,
        )
        created.append(screen)

    # I/O Monitor 화면에 IOPoint 태그 파생
    io_monitor = next((s for s in created if s.code == "IO_MONITOR"), None)
    if io_monitor:
        HMITag.objects.bulk_create(
            HMITag(screen=io_monitor, name=point.tag, signal_type=point.signal_type, io_point=point)
            for point in io_points
        )
        io_monitor.required_tags = [p.tag for p in io_points]
        io_monitor.save(update_fields=["required_tags", "updated_at"])

    return {"screens": len(created), "codes": [s.code for s in created]}
