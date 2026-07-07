"""I/O Estimation (PRD §13 I/O Design).

설비(DEVICE_LIST)와 센서 요구사항(SensorRequirement)으로 I/O 포인트를 산출한다.
설비별 표준 I/O 프로파일은 결정론적 규칙이다.
"""

from django.db import transaction

from apps.design.models import RiskLevel
from apps.design.services import create_design_decision
from apps.io_points.models import IOPoint
from apps.requirements.models import ProjectFact
from apps.requirements.selectors import project_state
from apps.requirements.services import ACTIVE_STATUSES

# 설비 유형별 표준 I/O 프로파일: [(신호, 접미사, 설명)]
DEVICE_IO_PROFILES = {
    "모터": [("DO", "RUN", "기동"), ("DI", "FB", "운전 피드백"), ("DI", "FAULT", "고장")],
    "펌프": [("DO", "RUN", "기동"), ("DI", "FB", "운전 피드백"), ("DI", "FAULT", "고장")],
    "밸브": [
        ("DO", "OPEN", "개방"),
        ("DI", "OPEN_FB", "개방 확인"),
        ("DI", "CLOSE_FB", "닫힘 확인"),
    ],
    "히터": [("DO", "ON", "가열"), ("DI", "FAULT", "고장")],
    "팬": [("DO", "RUN", "기동"), ("DI", "FB", "운전 피드백")],
    "컨베이어": [("DO", "RUN", "기동"), ("DI", "FB", "운전 피드백"), ("DI", "ESTOP", "비상정지")],
    "인버터": [
        ("AO", "SPEED", "속도 지령"),
        ("AI", "SPEED_FB", "속도 피드백"),
        ("DI", "FAULT", "고장"),
    ],
    "실린더": [("DO", "EXT", "전진"), ("DI", "EXT_FB", "전진 확인"), ("DI", "RET_FB", "후진 확인")],
}

# 센서 신호 → I/O 신호는 동일 매핑 (AI/DI)


def _flat_state(project):
    state = project_state(project_id=project.id)
    return {key: info["value"] for key, info in state.items()}


def _normalize_device(name: str) -> str:
    for key in DEVICE_IO_PROFILES:
        if key in name:
            return key
    return ""


@transaction.atomic
def estimate_io(*, project, actor=None):
    """DEVICE_LIST + 센서요구 → IOPoint 생성 (idempotent). 수량 집계를 반환한다."""
    project.io_points.all().delete()

    flat = _flat_state(project)
    devices = flat.get("DEVICE_LIST") or []
    if isinstance(devices, str):
        devices = [devices]

    device_fact = list(
        ProjectFact.objects.filter(
            project=project, fact_key="DEVICE_LIST", status__in=ACTIVE_STATUSES
        )
    )

    decision = create_design_decision(
        project=project,
        decision_type="IO_ESTIMATION",
        subject_type="IO_LIST",
        decision_value={"device_count": len(devices)},
        reason="설비 목록과 센서 요구사항으로 I/O를 산출",
        input_facts=device_fact,
        risk_level=RiskLevel.LOW,
        actor=actor,
    )

    used_tags = set()

    def add_point(signal, tag, description, source_type, source_ref, sensor_req=None):
        base_tag, n = tag, 1
        while tag in used_tags:
            n += 1
            tag = f"{base_tag}_{n}"
        used_tags.add(tag)
        return IOPoint.objects.create(
            project=project,
            decision=decision,
            tag=tag,
            signal_type=signal,
            description=description,
            source_type=source_type,
            source_ref=source_ref,
            sensor_requirement=sensor_req,
        )

    # 설비 I/O
    for index, device in enumerate(devices, start=1):
        normalized = _normalize_device(str(device))
        profile = DEVICE_IO_PROFILES.get(normalized, [("DI", "STATUS", "상태")])
        prefix = f"{normalized or 'DEV'}{index:02d}"
        for signal, suffix, desc in profile:
            add_point(signal, f"{prefix}_{suffix}", f"{device} {desc}", "DEVICE", str(device))

    # 센서 I/O
    for req in project.sensor_requirements.all():
        signal = req.signal_type or "AI"
        add_point(
            signal,
            f"{req.measurement_type}_{signal}",
            f"{req.measurement_type} 측정 ({req.measurement_principle})",
            "SENSOR",
            req.measurement_type,
            sensor_req=req,
        )

    counts = {
        signal: project.io_points.filter(signal_type=signal).count()
        for signal in ["DI", "DO", "AI", "AO"]
    }
    return {"counts": counts, "total": sum(counts.values())}
