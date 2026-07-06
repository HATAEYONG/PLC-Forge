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

## 2026-07-06 — Phase 1: Core Domain (사용자 승인 후 착수)
- **T1.1** `apps.accounts` 커스텀 User(UUID PK, PRD §4 역할 7종) + SimpleJWT
  (`/api/auth/token/`, `/refresh/`, `/me/`), 기본 권한 IsAuthenticated (D1: JWT 확정)
- **T1.2** `apps.companies` Company CRUD
- **T1.3** `apps.projects` Project CRUD (company FK, code unique, 상태 7종, created_by 자동)
- **T1.4** `apps.interview` Question(§8.2 전체 필드 + §8.3/§8.4 choices, (code,version) unique,
  answer_schema JSON Schema 검증), AnswerOption, InterviewSession,
  `POST /sessions/{id}/answer/` (Service Layer 경유, 진행 중이 아닌 세션은 409)
- **T1.5** `apps.requirements` ProjectFact(§10) + FactStatus 상태기계
  (서비스에서 전이 강제, 위반 시 409 invalid_fact_transition),
  동일 key 재생성 시 version 증가 + 이전 활성 Fact SUPERSEDED,
  ProjectState Projection selector
- **T1.6** `apps.knowledge` KnowledgeItem(§11, 8계층) CRUD
- **T1.7** `apps.design` Rule(§12, HARD/RECOMMENDATION) + DesignDecision(§13,
  M2M 조인 테이블 Traceability). **근거(입력 Fact/규칙/지식) 0개 또는 reason 없으면 생성 거부.**
  HIGH/CRITICAL risk는 approval_required 자동 설정
- **T1.8** `apps.audit` AuditEvent(§25) + `record_event()` — Fact 생성/전이, 답변 제출,
  Decision 생성 시 기록. API는 읽기 전용
- **T1.9** 라우터 배선(§29 경로), 페이지네이션(20), DomainError→통일 오류 포맷 매핑

### 검증 결과 (컨테이너 내 실측)
- pytest **35 passed** (인증 3, 회사 2, 프로젝트 2, 질문 4, 세션 3, Fact 6, 지식 1, 규칙 1,
  Decision 5, 감사 2, Phase 0 기존 6), ruff clean, `makemigrations --check` clean
- 실서버 스모크: JWT 발급 → Bearer로 Company 생성/조회(한글 정상) → 미인증 요청이
  통일 오류 포맷 401 반환
- AUTH_USER_MODEL 변경으로 개발 DB 재생성 (운영 데이터 없음, 문제 없음)

### 다음 단계
- 사용자 승인 후 Phase 2 (Question Engine) 착수
