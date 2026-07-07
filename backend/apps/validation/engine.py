"""Validation Engine (PRD §22).

설계 산출물의 정합성·커버리지·안전을 검사한다. 각 검사는 (severity, code, title,
description, related_objects, recommended_action) 딕셔너리 목록을 반환한다.
CRITICAL Finding이 존재하면 Vendor Generation을 금지한다 (§22, §33-14).
"""

from collections import Counter

from django.db import transaction

from apps.requirements.selectors import project_state
from apps.validation.models import Severity, ValidationFinding


def _f(severity, code, title, description="", related=None, action=""):
    return {
        "severity": severity,
        "code": code,
        "title": title,
        "description": description,
        "related_objects": related or [],
        "recommended_action": action,
    }


# ── 개별 검사기 ─────────────────────────────────────────
def check_missing_requirement(project, state):
    findings = []
    if not state.get("DEVICE_LIST"):
        findings.append(
            _f(
                Severity.ERROR,
                "MISSING_DEVICE_LIST",
                "설비 목록 미확보",
                "DEVICE_LIST Fact가 없어 I/O·PLC 산정이 불완전합니다.",
                action="인터뷰에서 설비 목록을 확보하세요.",
            )
        )
    if not state.get("MEASUREMENT_REQUIREMENTS"):
        findings.append(
            _f(
                Severity.WARNING,
                "MISSING_MEASUREMENT",
                "측정 요구 미확보",
                "측정 항목이 없어 센서 설계가 비어 있을 수 있습니다.",
            )
        )
    return findings


def check_missing_sensor(project, state):
    findings = []
    measurements = state.get("MEASUREMENT_REQUIREMENTS") or []
    if isinstance(measurements, str):
        measurements = [measurements]
    designed = set(project.sensor_requirements.values_list("measurement_type", flat=True))
    for measurement in measurements:
        if measurement not in designed:
            findings.append(
                _f(
                    Severity.ERROR,
                    "MISSING_SENSOR",
                    f"{measurement} 센서 미설계",
                    f"측정 요구 '{measurement}'에 대한 센서 요구사항이 없습니다.",
                    related=[measurement],
                    action="센서 설계를 재생성하세요(generate-design?stage=sensor).",
                )
            )
    return findings


def check_io_consistency(project, state):
    findings = []
    for req in project.sensor_requirements.all():
        signal = req.signal_type
        if signal and not project.io_points.filter(sensor_requirement=req).exists():
            findings.append(
                _f(
                    Severity.WARNING,
                    "SENSOR_WITHOUT_IO",
                    f"{req.measurement_type} I/O 누락",
                    "센서 요구사항에 대응하는 I/O 포인트가 없습니다.",
                    related=[req.measurement_type],
                )
            )
    return findings


def check_duplicate_tag(project, state):
    findings = []
    tags = list(project.io_points.values_list("tag", flat=True))
    dups = [tag for tag, n in Counter(tags).items() if n > 1]
    for tag in dups:
        findings.append(
            _f(
                Severity.CRITICAL,
                "DUPLICATE_TAG",
                f"중복 I/O 태그: {tag}",
                "동일 태그가 중복되어 주소 충돌이 발생합니다.",
                related=[tag],
                action="I/O 태그를 유일하게 재생성하세요.",
            )
        )
    return findings


def check_signal_type_mismatch(project, state):
    findings = []
    valid = {"DI", "DO", "AI", "AO"}
    for point in project.io_points.exclude(signal_type__in=valid):
        findings.append(
            _f(
                Severity.ERROR,
                "SIGNAL_TYPE_INVALID",
                f"잘못된 신호 유형: {point.tag}",
                f"신호 유형 '{point.signal_type}'은 허용되지 않습니다.",
                related=[point.tag],
            )
        )
    return findings


def check_plc_capacity(project, state):
    findings = []
    sizing = project.plc_sizing_results.first()
    if not sizing and project.io_points.exists():
        findings.append(
            _f(
                Severity.WARNING,
                "NO_PLC_SIZING",
                "PLC Sizing 미수행",
                "I/O가 존재하지만 PLC Sizing 결과가 없습니다.",
                action="generate-design?stage=plc 를 실행하세요.",
            )
        )
    if sizing and not sizing.candidates.filter(accepted=True).exists():
        findings.append(
            _f(
                Severity.ERROR,
                "NO_PLC_CANDIDATE",
                "채택 가능한 PLC 후보 없음",
                "Sizing 요건을 만족하는 채택 후보가 없습니다.",
            )
        )
    return findings


def check_alarm_coverage(project, state):
    findings = []
    required = project.design_decisions.filter(decision_type="ALARM_REQUIREMENT").count()
    actual = project.alarms.count()
    if required and actual < required:
        findings.append(
            _f(
                Severity.ERROR,
                "ALARM_COVERAGE",
                "알람 커버리지 부족",
                f"알람 요구 {required}건 중 {actual}건만 정의되었습니다.",
                action="알람을 재생성하세요(generate-design?stage=alarm).",
            )
        )
    return findings


def check_interlock_coverage(project, state):
    findings = []
    required = project.design_decisions.filter(decision_type="INTERLOCK_REQUIREMENT").count()
    actual = project.interlocks.count()
    if required and actual < required:
        findings.append(
            _f(
                Severity.CRITICAL,
                "INTERLOCK_COVERAGE",
                "인터록 커버리지 부족",
                f"인터록 요구 {required}건 중 {actual}건만 정의되었습니다. 안전 관련 누락입니다.",
                action="인터록을 재생성하고 안전 검토를 수행하세요.",
            )
        )
    return findings


def check_sequence_dead_end(project, state):
    findings = []
    for sequence in project.sequences.prefetch_related("steps"):
        steps = list(sequence.steps.all())
        step_nos = {s.step_no for s in steps}
        for step in steps:
            # 마지막 스텝이 아닌데 next_step이 없으면 dead-end
            if step.next_step is None and step != steps[-1]:
                findings.append(
                    _f(
                        Severity.ERROR,
                        "SEQUENCE_DEAD_END",
                        f"시퀀스 dead-end: {sequence.code} step {step.step_no}",
                        "다음 스텝이 지정되지 않았습니다.",
                        related=[sequence.code],
                    )
                )
            if step.next_step is not None and step.next_step not in step_nos:
                findings.append(
                    _f(
                        Severity.ERROR,
                        "SEQUENCE_UNREACHABLE",
                        f"존재하지 않는 next_step: {sequence.code} step {step.step_no}",
                        f"next_step {step.next_step}가 시퀀스에 없습니다.",
                        related=[sequence.code],
                    )
                )
    return findings


def check_sequence_timeout(project, state):
    findings = []
    for sequence in project.sequences.prefetch_related("steps"):
        for step in sequence.steps.all():
            if step.timeout_seconds and not step.timeout_alarm:
                findings.append(
                    _f(
                        Severity.WARNING,
                        "SEQUENCE_TIMEOUT_NO_ALARM",
                        f"타임아웃 알람 미지정: {sequence.code} step {step.step_no}",
                        "타임아웃은 있으나 타임아웃 알람이 없습니다.",
                        related=[sequence.code],
                    )
                )
    return findings


def check_unsafe_bypass(project, state):
    findings = []
    for interlock in project.interlocks.filter(safety_related=True, bypass_allowed=True):
        if not interlock.bypass_permission:
            findings.append(
                _f(
                    Severity.CRITICAL,
                    "UNSAFE_BYPASS",
                    f"안전 인터록 무권한 바이패스: {interlock.code}",
                    "안전 관련 인터록의 바이패스에 권한 정책이 없습니다.",
                    related=[interlock.code],
                    action="바이패스 권한/기록 정책을 지정하거나 바이패스를 금지하세요.",
                )
            )
    return findings


def check_fat_sat_coverage(project, state):
    findings = []
    for phase, code in [("FAT", "FAT_COVERAGE"), ("SAT", "SAT_COVERAGE")]:
        for alarm in project.alarms.all():
            required = alarm.fat_test_required if phase == "FAT" else alarm.sat_test_required
            if (
                required
                and not project.test_cases.filter(
                    phase=phase, source_type="ALARM", source_ref=alarm.code
                ).exists()
            ):
                findings.append(
                    _f(
                        Severity.WARNING,
                        code,
                        f"{phase} 미커버 알람: {alarm.code}",
                        f"{phase} 테스트가 없는 알람이 있습니다.",
                        related=[alarm.code],
                    )
                )
        for interlock in project.interlocks.all():
            if not project.test_cases.filter(
                phase=phase, source_type="INTERLOCK", source_ref=interlock.code
            ).exists():
                findings.append(
                    _f(
                        Severity.ERROR,
                        code,
                        f"{phase} 미커버 인터록: {interlock.code}",
                        f"{phase} 테스트가 없는 인터록이 있습니다.",
                        related=[interlock.code],
                    )
                )
    return findings


def check_traceability_coverage(project, state):
    findings = []
    # 근거(입력 Fact/규칙/지식) 없는 DesignDecision 탐지
    for decision in project.design_decisions.prefetch_related(
        "input_facts", "rules", "knowledge_items"
    ):
        if not (
            decision.input_facts.exists()
            or decision.rules.exists()
            or decision.knowledge_items.exists()
        ):
            findings.append(
                _f(
                    Severity.ERROR,
                    "TRACEABILITY_GAP",
                    f"근거 없는 설계 결정: {decision.decision_type}",
                    "입력 Fact/규칙/지식 연결이 없습니다.",
                    related=[str(decision.id)],
                )
            )
    return findings


CHECKS = [
    check_missing_requirement,
    check_missing_sensor,
    check_io_consistency,
    check_duplicate_tag,
    check_signal_type_mismatch,
    check_plc_capacity,
    check_alarm_coverage,
    check_interlock_coverage,
    check_sequence_dead_end,
    check_sequence_timeout,
    check_unsafe_bypass,
    check_fat_sat_coverage,
    check_traceability_coverage,
]


@transaction.atomic
def run_validation(project):
    """전 검사를 실행하고 ValidationFinding을 갱신한다 (idempotent). 요약을 반환."""
    project.validation_findings.all().delete()
    flat = {key: info["value"] for key, info in project_state(project_id=project.id).items()}

    findings = []
    for check in CHECKS:
        findings.extend(check(project, flat))

    ValidationFinding.objects.bulk_create(
        ValidationFinding(project=project, **finding) for finding in findings
    )

    counts = Counter(f["severity"] for f in findings)
    return {
        "total": len(findings),
        "by_severity": {sev: counts.get(sev, 0) for sev in Severity.values},
        "has_critical": counts.get(Severity.CRITICAL, 0) > 0,
    }


def has_blocking_findings(project) -> bool:
    """CRITICAL Finding이 미해결(OPEN/ACKNOWLEDGED) 상태로 존재하는지."""
    return project.validation_findings.filter(
        severity=Severity.CRITICAL, status__in=["OPEN", "ACKNOWLEDGED"]
    ).exists()
