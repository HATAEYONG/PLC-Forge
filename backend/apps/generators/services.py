"""Vendor Code Generation 서비스 (PRD §21).

CRITICAL Finding이 있으면 어댑터 실행 자체를 차단한다 (§22, §33-14).
"""

from apps.audit.services import record_event
from apps.generators.adapters.ls_electric import LSElectricAdapter
from apps.generators.ir import build_ir, validate_ir
from apps.validation.services import assert_generation_allowed
from core.exceptions import DomainError

ADAPTERS = {
    LSElectricAdapter.vendor_key: LSElectricAdapter,
    # Siemens / Mitsubishi 어댑터는 PRD §21 순서에 따라 후속 추가
}


def generate_vendor_package(*, project, vendor="ls", actor=None):
    """IR 생성 → 검증 → 벤더 어댑터 실행. CRITICAL 검증 통과가 선행 조건이다."""
    adapter_cls = ADAPTERS.get(vendor)
    if adapter_cls is None:
        raise DomainError(
            f"지원하지 않는 벤더: '{vendor}'. 가능: {sorted(ADAPTERS)}",
            code="unknown_vendor",
        )

    # 1) CRITICAL 차단 게이트
    assert_generation_allowed(project)

    # 2) Vendor Independent IR 생성 + 스키마 검증
    ir = build_ir(project)
    validate_ir(ir)

    # 3) 어댑터 실행
    adapter = adapter_cls()
    result = adapter.package_output(ir)

    record_event(
        actor=actor,
        action="VENDOR_CODE_GENERATED",
        object_type="Project",
        object_id=project.id,
        after={
            "vendor": adapter.vendor_name,
            "files": sorted(result["files"].keys()),
            "signal_count": result["mapping_report"]["signal_count"],
        },
    )
    return {"vendor": adapter.vendor_name, "ir": ir, **result}
