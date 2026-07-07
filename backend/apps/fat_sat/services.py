"""FAT/SAT Test Case 생성 (PRD §24).

요구·센서·알람·인터록·시퀀스로부터 테스트 케이스를 자동 생성한다. 각 테스트는
source_type/source_ref로 원 산출물까지 역추적된다. FAT는 공장, SAT는 현장 검증.
"""

from django.db import transaction

from apps.fat_sat.models import TestCase, TestPhase


@transaction.atomic
def generate_tests(*, project, actor=None):
    """설계 산출물로 FAT/SAT 테스트를 생성한다 (idempotent)."""
    project.test_cases.all().delete()

    fat, sat = [], []

    def add(bucket, phase, prefix, seq, **kwargs):
        bucket.append(
            TestCase(project=project, phase=phase, test_id=f"{prefix}-{seq:03d}", **kwargs)
        )

    # 센서 → 검교정/검증
    for i, req in enumerate(project.sensor_requirements.all(), start=1):
        add(
            fat,
            TestPhase.FAT,
            "FAT-SEN",
            i,
            category="SENSOR",
            precondition=f"{req.measurement_type} 센서 시뮬레이터 연결",
            procedure=f"{req.measurement_type} 입력을 0-100%로 인가하며 값 확인",
            expected_result="HMI/PLC 값이 입력과 일치(허용오차 내)",
            source_type="SENSOR",
            source_ref=req.measurement_type,
        )
        add(
            sat,
            TestPhase.SAT,
            "SAT-SEN",
            i,
            category="SENSOR",
            precondition=f"{req.measurement_type} 센서 현장 설치 완료",
            procedure="실제 공정값과 기준기 비교",
            expected_result="현장 실측과 표시값 일치",
            source_type="SENSOR",
            source_ref=req.measurement_type,
        )

    # 알람 → 시뮬레이션/실동작
    for i, alarm in enumerate(project.alarms.all(), start=1):
        if alarm.fat_test_required:
            add(
                fat,
                TestPhase.FAT,
                "FAT-ALM",
                i,
                category="ALARM",
                precondition="시스템 정상 운전",
                procedure=f"{alarm.condition} 조건을 강제 발생",
                expected_result=f"{alarm.code} 알람 발생, 우선순위 {alarm.priority}",
                source_type="ALARM",
                source_ref=alarm.code,
            )
        if alarm.sat_test_required:
            add(
                sat,
                TestPhase.SAT,
                "SAT-ALM",
                i,
                category="ALARM",
                precondition="현장 운전 상태",
                procedure=f"{alarm.condition} 실제 조건 재현/모의",
                expected_result=f"{alarm.code} 알람 정상 동작 및 조치 안내",
                source_type="ALARM",
                source_ref=alarm.code,
            )

    # 인터록 → 트립 시험
    for i, interlock in enumerate(project.interlocks.all(), start=1):
        add(
            fat,
            TestPhase.FAT,
            "FAT-ILK",
            i,
            category="INTERLOCK",
            precondition=f"{interlock.protected_device} 운전 중",
            procedure=f"인터록 조건({interlock.condition}) 강제 성립",
            expected_result=f"{interlock.effect} 동작, 복귀조건 {interlock.reset_condition}",
            source_type="INTERLOCK",
            source_ref=interlock.code,
        )
        add(
            sat,
            TestPhase.SAT,
            "SAT-ILK",
            i,
            category="INTERLOCK",
            precondition=f"{interlock.protected_device} 현장 운전",
            procedure="실제 보호 조건 모의 시험",
            expected_result=f"{interlock.effect} 정상 동작",
            source_type="INTERLOCK",
            source_ref=interlock.code,
        )

    # 시퀀스 → 스텝 진행 시험
    seq_index = 1
    for sequence in project.sequences.all():
        for step in sequence.steps.all():
            add(
                fat,
                TestPhase.FAT,
                "FAT-SEQ",
                seq_index,
                category="SEQUENCE",
                precondition=f"{sequence.name} Step{step.step_no} 진입 조건 충족",
                procedure=f"'{step.name}' 실행 및 완료조건 확인",
                expected_result=step.completion_condition or "정상 완료 후 다음 스텝 진행",
                source_type="SEQUENCE",
                source_ref=f"{sequence.code}#{step.step_no}",
            )
            seq_index += 1

    TestCase.objects.bulk_create(fat + sat)
    return {
        "fat": len(fat),
        "sat": len(sat),
        "total": len(fat) + len(sat),
    }
