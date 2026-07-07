"""PLC Sizing (PRD §15).

I/O 개수뿐 아니라 고속카운터/모션/PID/Safety/이중화/확장여유/기존벤더/유지보수 역량 등을
반영해 PLC 등급과 후보를 산출한다. Rejected Candidates and Reasons를 포함한다.
"""

import math

from django.db import transaction

from apps.design.models import RiskLevel
from apps.design.services import create_design_decision
from apps.plc_design.models import PLCCandidate, PLCClass, PLCSizingResult
from apps.requirements.models import ProjectFact
from apps.requirements.selectors import project_state
from apps.requirements.services import ACTIVE_STATUSES

# 후보 벤더 카탈로그(등급별). 기존 표준 벤더가 있으면 우선.
VENDOR_FAMILIES = {
    PLCClass.MICRO: [("LS ELECTRIC", "XGB"), ("Siemens", "S7-1200"), ("Mitsubishi", "FX5U")],
    PLCClass.COMPACT: [("LS ELECTRIC", "XGB"), ("Siemens", "S7-1200"), ("Mitsubishi", "FX5U")],
    PLCClass.MODULAR: [("LS ELECTRIC", "XGI/XGK"), ("Siemens", "S7-1500"), ("Mitsubishi", "iQ-R")],
    PLCClass.HIGH_END: [
        ("Siemens", "S7-1500R/H"),
        ("LS ELECTRIC", "XGI 이중화"),
        ("Mitsubishi", "iQ-R 이중화"),
    ],
}

VENDOR_KEY_MAP = {
    "LS": "LS ELECTRIC",
    "SIEMENS": "Siemens",
    "MITSUBISHI": "Mitsubishi",
    "AB": "Allen-Bradley",
}


def _flat_state(project):
    state = project_state(project_id=project.id)
    return {key: info["value"] for key, info in state.items()}


def _io_counts(project):
    return {
        signal: project.io_points.filter(signal_type=signal).count()
        for signal in ["DI", "DO", "AI", "AO"]
    }


def _decide_class(total_io_with_margin, factors):
    """등급 판정 (I/O 규모 + 요소)."""
    if factors.get("redundancy"):
        return PLCClass.HIGH_END
    if total_io_with_margin > 256 or factors.get("motion_axis") or factors.get("safety_io"):
        return PLCClass.MODULAR
    if total_io_with_margin > 64 or factors.get("pid_loops") or factors.get("remote_io"):
        return PLCClass.COMPACT
    return PLCClass.MICRO


@transaction.atomic
def size_plc(*, project, actor=None):
    """I/O 집계 + §15 요소로 PLC 등급/후보를 산출한다 (idempotent)."""
    project.plc_sizing_results.all().delete()

    flat = _flat_state(project)
    counts = _io_counts(project)
    margin = 20
    total_io = sum(counts.values())
    total_with_margin = math.ceil(total_io * (1 + margin / 100))

    factors = {
        "pid_loops": bool(
            flat.get("HEATED_TANK_COUNT") or "HEATING" in (flat.get("PROCESSES") or [])
        ),
        "motion_axis": bool(flat.get("SERVO_USED")),
        "safety_io": bool(flat.get("ESTOP_REQUIRED")),
        "remote_io": bool(flat.get("SCADA_REQUIRED")),
        "redundancy": bool(flat.get("REDUNDANCY_REQUIRED")),
        "future_expansion": bool(flat.get("FUTURE_EXPANSION")),
        "existing_vendor": flat.get("EXISTING_PLC_VENDOR"),
        "maintenance": flat.get("MAINTENANCE_CAPABILITY"),
    }
    if factors["future_expansion"]:
        margin = 30
        total_with_margin = math.ceil(total_io * (1 + margin / 100))

    required_class = _decide_class(total_with_margin, factors)

    reason_parts = [
        f"I/O 합계 {total_io}점(DI {counts['DI']}/DO {counts['DO']}/"
        f"AI {counts['AI']}/AO {counts['AO']}) + 여유율 {margin}% → {total_with_margin}점"
    ]
    if factors["redundancy"]:
        reason_parts.append("이중화 요구 → 고성능 등급")
    if factors["safety_io"]:
        reason_parts.append("Safety I/O 필요")
    if factors["pid_loops"]:
        reason_parts.append("PID 루프 필요(가열)")

    source_facts = list(
        ProjectFact.objects.filter(
            project=project,
            fact_key__in=[
                "DEVICE_LIST",
                "EXISTING_PLC_VENDOR",
                "REDUNDANCY_REQUIRED",
                "FUTURE_EXPANSION",
                "ESTOP_REQUIRED",
            ],
            status__in=ACTIVE_STATUSES,
        )
    )

    decision = create_design_decision(
        project=project,
        decision_type="PLC_SIZING",
        subject_type="PLC",
        decision_value={"required_class": required_class, "total_io": total_io, "factors": factors},
        reason=". ".join(reason_parts),
        input_facts=source_facts,
        risk_level=RiskLevel.MEDIUM,
        actor=actor,
    )

    sizing = PLCSizingResult.objects.create(
        project=project,
        decision=decision,
        di_count=counts["DI"],
        do_count=counts["DO"],
        ai_count=counts["AI"],
        ao_count=counts["AO"],
        spare_margin_percent=margin,
        factors_json=factors,
        required_class=required_class,
        minimum_spec_json={
            "min_di": counts["DI"],
            "min_do": counts["DO"],
            "min_ai": counts["AI"],
            "min_ao": counts["AO"],
            "recommended_io_slots_with_margin": total_with_margin,
            "pid_loops": factors["pid_loops"],
            "safety": factors["safety_io"],
            "redundancy": factors["redundancy"],
        },
        selection_reason=". ".join(reason_parts),
    )

    # 후보 + Rejected Candidates and Reasons (§15)
    existing_vendor = VENDOR_KEY_MAP.get(str(factors["existing_vendor"] or "").upper())
    for vendor, family in VENDOR_FAMILIES[required_class]:
        accepted = True
        reason = f"{required_class} 등급 요건 충족"
        if existing_vendor and vendor != existing_vendor:
            accepted = False
            reason = f"기존 표준 벤더({existing_vendor})와 상이하여 후순위"
        elif existing_vendor and vendor == existing_vendor:
            reason = f"기존 표준 벤더({existing_vendor}) — 유지보수/예비품 유리로 우선 채택"
        PLCCandidate.objects.create(
            sizing=sizing, vendor=vendor, family=family, accepted=accepted, reason=reason
        )

    return sizing
