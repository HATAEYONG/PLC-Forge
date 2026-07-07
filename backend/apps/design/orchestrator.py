"""Design Engine 오케스트레이션 (PRD §13).

인터뷰 상태 + 규칙 결과를 바탕으로 설계 산출물을 순서대로 생성한다.
Phase 4-A 범위: sensor → io → plc. (communication/hmi/alarm 등은 Phase 4-B/4-C)
"""

from apps.communications.services import generate_communication
from apps.hmi_design.services import generate_hmi
from apps.io_points.services import estimate_io
from apps.plc_design.services import size_plc
from apps.sensors.services import generate_sensor_requirements
from core.exceptions import DomainError

# 각 stage의 의존 순서 (앞 단계 산출물이 뒤 단계 입력이 됨)
STAGE_ORDER = ["sensor", "io", "plc", "comm", "hmi"]


def generate_design(*, project, stage="all", actor=None):
    """지정한 stage(들)의 설계를 생성한다. stage='all'이면 전체를 순서대로 실행."""
    if stage not in (*STAGE_ORDER, "all"):
        raise DomainError(f"지원하지 않는 stage: '{stage}'", code="unknown_stage")
    stages = STAGE_ORDER if stage == "all" else [stage]
    summary = {}

    for current in stages:
        if current == "sensor":
            requirements = generate_sensor_requirements(project=project, actor=actor)
            summary["sensor"] = {"count": len(requirements)}
        elif current == "io":
            summary["io"] = estimate_io(project=project, actor=actor)
        elif current == "plc":
            sizing = size_plc(project=project, actor=actor)
            summary["plc"] = {
                "required_class": sizing.required_class,
                "candidates": sizing.candidates.count(),
            }
        elif current == "comm":
            summary["comm"] = generate_communication(project=project, actor=actor)
        elif current == "hmi":
            summary["hmi"] = generate_hmi(project=project, actor=actor)
    return summary
