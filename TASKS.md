# TASKS.md — Phase 6-C: Excel Export · E2E 정식화

**목표:** 설계 산출물을 Excel(.xlsx)로 내보내고(MVP 26번), 프론트 Export 버튼과
Playwright E2E 해피패스를 CI에 편입한다. (이전 내역은 WORKLOG.md 참조)

## T6C.1 documents 앱 — Excel Export (백엔드)
- `openpyxl` 기반 워크북 생성: I/O List / Alarm / Interlock / Cause&Effect / FAT / SAT 시트
- `GET /api/projects/{id}/export/` → .xlsx 스트리밍(한글 파일명, UTF-8)
- ✓ 시트 구성·행수·한글 셀 테스트

## T6C.2 프론트 Export 버튼
- 설계 탭 또는 별도 위치에 Export 버튼 → 인증 토큰 포함 다운로드
- ✓ 다운로드 트리거 테스트(모킹)

## T6C.3 Playwright E2E 정식화
- `@playwright/test` devDependency + playwright.config(신형 headless, executablePath)
- 해피패스: 로그인 → 프로젝트 → 인터뷰 → 설계 생성 → 검증 → 승인 → Export
- `npm run e2e` 스크립트, CI 잡 추가(백엔드 postgres + 서버 기동)

## Phase 6-C Exit Checklist
- [ ] 백엔드 pytest green(Export 포함), 프론트 vitest/lint/build green
- [ ] .xlsx 다운로드 동작(시트 구성 확인)
- [ ] Playwright 해피패스 통과 + CI 편입
- [ ] WORKLOG.md 갱신 + 사용자 승인 → Phase 7
