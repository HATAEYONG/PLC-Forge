"""Validation 서비스 — Vendor Generation 차단 게이트 (PRD §22, §33-14)."""

from apps.validation.engine import has_blocking_findings, run_validation
from core.exceptions import DomainError

__all__ = ["run_validation", "has_blocking_findings", "assert_generation_allowed"]


def assert_generation_allowed(project):
    """CRITICAL Finding이 있으면 Vendor Code Generation을 차단한다.

    검증이 수행된 적 없으면 먼저 실행한다.
    """
    if not project.validation_findings.exists():
        run_validation(project)
    if has_blocking_findings(project):
        blocking = list(
            project.validation_findings.filter(
                severity="CRITICAL", status__in=["OPEN", "ACKNOWLEDGED"]
            ).values_list("code", flat=True)
        )
        raise DomainError(
            "CRITICAL 검증 항목이 존재하여 벤더 코드 생성이 차단되었습니다.",
            code="critical_findings_block_generation",
            status_code=409,
            details={"critical_findings": blocking},
        )
