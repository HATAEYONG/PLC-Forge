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

## 2026-07-06 — Phase 2: Question Engine (사용자 승인 후 착수)
- **T2.1** `core/jsonlogic.py` — 최소 JSONLogic 평가기(var/비교/and·or·!/in/missing) (D4 확정).
  Question 조건과 Rule 조건이 공용
- **T2.2** 후보 필터링 — is_active + 미답변 + required/exclusion + 업종/공정 적용성
- **T2.3** 질문 점수화(§8.5) — 8개 가점 요소 + 3개 감점 요소, 가중치 상수화(콜드스타트, R3)
- **T2.4** `QuestionSelectionLog` + `GET /next-question/` — 최고점 질문 + 점수 내역·선택 이유 저장
- **T2.5** 종료조건(§8.6) `completion.py` — Critical/Safety 커버리지 + 설계별 필수 Fact +
  미해결 충돌 없음. 미충족 시 계속 질문, `POST /complete/`는 미충족 시 409
- **T2.6** Answer Processing 파이프라인(§9, Rule-based, LLM 미사용):
  Validation(JSON Schema) → Normalization → Unit Conversion(℃/℉) →
  한국어 Entity Extraction(정규식) → Fact Generation(confidence) →
  Contradiction Detection(상충 시 양쪽 CONFLICTED) → Projection
- **T2.7** 세션 API 확장 — `/next-question/ /facts/ /state/ /progress/ /complete/`,
  답변 응답에 생성 Fact 포함
- **T2.8** 초기 질문 데이터 **60개**(식품·수처리 우선, PRD §28 Phase 1 목표 50개 초과 달성)
  + `load_questions` 관리 명령(idempotent). ⚠️ SAFETY/INTERLOCK 질문 8종은 전문가 검토 대상(D6)

### 검증 결과 (컨테이너 내 실측)
- pytest **67 passed**, ruff clean, 마이그레이션 drift 없음
- 핵심 시나리오 테스트(LLM 미사용): "탱크가 3개 있고 그중 두 개는 80도 정도이며 세척할 때
  증기가 생깁니다" → TANK_COUNT=3, HEATED_TANK_COUNT=2, MAX_TEMPERATURE_APPROX=80C,
  CIP_REQUIRED=True, STEAM_PRESENT_DURING_CIP=True
- 라이브 스모크: 첫 next-question이 CRITICAL 안전 질문(Q-SAF-001)을 점수근거
  "핵심 정보 누락(+100), 기본 우선순위(+95), 안전 위험 탐지(+40)"와 함께 선택,
  자연어 답변에서 Fact 6종 추출 후 Projection 반영 확인
- 참고: 세션 중 컨테이너의 PostgreSQL가 재기동되었으나 pgdata 볼륨으로 데이터 보존됨

### ⚠️ 사용자 검토 요청 (D6, PRD §33-5)
- 초기 질문 데이터의 **안전 관련 질문 8종**(Q-SAF-001~004, Q-ILK-001, Q-ALM-003 등)은
  자동화 전문가 검토 후 확정 필요. `backend/apps/interview/questions_seed.py` 참조

### 다음 단계
- 사용자 승인 후 Phase 3 (Knowledge & Rule Engine) 착수
