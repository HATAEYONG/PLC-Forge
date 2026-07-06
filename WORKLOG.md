# WORKLOG.md

## 2026-07-06 — 계획 수립
- 저장소 `hataeyong/plc-forge` 확정 (church-ai에서 분리)
- PRD §34 산출물 작성: PLAN / TASKS / RISKS / ACCEPTANCE_CRITERIA / DECISIONS_REQUIRED

## 2026-07-06 — Phase 0: Repository Bootstrap
- **T0.1** `.gitignore`, `.editorconfig`, README 갱신
- **T0.2** Django 5.2 + DRF 3.17 스캐폴드, settings 분리(base/dev/prod), 환경변수 로딩, `.env.example`
- **T0.3** 통일 API 오류 포맷 `{"error": {code, message, details}}` — DRF EXCEPTION_HANDLER + 테스트 3건
- **T0.4** `docker-compose.yml` (postgres:16 + backend + frontend), Dockerfile 2종
- **T0.5** `GET /api/health/` (DB 연결 확인 포함) + 테스트
- **T0.6** pytest + pytest-django + factory-boy, ruff (lint+format), Makefile 타깃
- **T0.7** 한글 UTF-8 왕복 테스트 — ORM/API 경로 각 1건 (`KeyValueEntry` 부트스트랩 검증 모델)
- **T0.8** Vite 6 + React 18 + TS 스캐폴드, 라우터, `/api` dev proxy, health 표시 페이지
- **T0.9** Vitest + React Testing Library 테스트 2건, ESLint(flat) + Prettier + tsc 클린
- **T0.10** GitHub Actions CI (`.github/workflows/ci.yml`) — backend/frontend 병렬 잡
- **T0.11** WORKLOG.md 초기화 (본 문서)

### 검증 결과 (컨테이너 내 실측)
- PostgreSQL 16 (UTF8) 기동 → `migrate` 성공
- backend pytest **6 passed**, ruff clean
- 실서버 확인: `/api/health/` 200 `{status:ok, db:true}`, 한글 KV 왕복 정상,
  404 오류가 통일 포맷으로 반환
- frontend vitest **2 passed**, eslint/tsc/prettier clean
- Vite dev server → `/api` 프록시 경유 backend 응답 확인 (풀스택 연동)
- 참고: 이 개발 컨테이너에는 Docker 데몬이 없어 `docker compose up` 자체는 미검증
  (파일은 표준 구성, CI의 postgres service로 동일 경로 검증)

### 다음 단계
- 사용자 승인 후 Phase 1 (Core Domain) 착수 — TASKS.md를 Phase 1 작업으로 갱신 예정
