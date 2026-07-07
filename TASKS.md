# TASKS.md — Phase 5: Validation & Approval

**목표:** 설계 산출물을 검증(§22)하고, CRITICAL Finding 시 Vendor Generation을 차단하며,
승인 워크플로(§23)를 구현한다. (이전 내역은 WORKLOG.md 참조)

## T5.1 validation 앱 — ValidationFinding (§22)
- `ValidationFinding`: severity(INFO/WARNING/ERROR/CRITICAL)/code/title/description/
  related_objects/recommended_action/status
- ✓ 모델·상태 테스트

## T5.2 Validation Engine — 검사기 (§22)
- 검사 항목(각 함수): Missing Requirement / Missing Sensor / I/O Consistency /
  Duplicate Tag / Signal Type Mismatch / PLC Capacity / Alarm Coverage /
  Interlock Coverage / Sequence Dead-End / Sequence Timeout / Unsafe Bypass /
  FAT Coverage / SAT Coverage / Traceability Coverage
- `run_validation(project)` — 전 검사 실행 → ValidationFinding 갱신(idempotent)
- ✓ 각 검사 양성/음성 테스트

## T5.3 CRITICAL 차단 (§22, §33-14)
- `assert_generation_allowed(project)` — CRITICAL Finding 있으면 DomainError(409)
- `POST /projects/{id}/validate/`, `GET /projects/{id}/validation-findings/`
- ✓ CRITICAL 존재 시 vendor generation 차단 테스트

## T5.4 approvals 앱 — Approval Workflow (§23)
- `Approval`: target(11종)/status(DRAFT→IN_REVIEW→APPROVED/REJECTED/SUPERSEDED)/
  approver/reason + ApprovalHistory
- 상태기계 강제(건너뛰기 거부), Safety 대상은 승인 없이 확정 불가
- 모든 승인/거절 AuditEvent 기록
- ✓ 상태 전이 허용/거부, 감사 기록 테스트

## T5.5 Review Queue + API
- `GET /projects/{id}/approvals/`, `POST .../submit-review/`, 승인/거절 액션
- CRITICAL Finding 있으면 최종 승인(Vendor Code Generation 등) 차단
- ✓ 리뷰 큐 + 승인 API 테스트

## Phase 5 Exit Checklist
- [ ] 전체 pytest green, ruff clean, 마이그레이션 drift 없음
- [ ] §22 각 검사 항목 양성/음성 테스트
- [ ] CRITICAL Finding 시 Vendor Generation 차단 (핵심)
- [ ] Approval 상태기계 강제 + Safety 승인 필수
- [ ] WORKLOG.md 갱신 + 사용자 승인 → Phase 6
