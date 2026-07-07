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

## 2026-07-07 — Phase 3: Knowledge & Rule Engine (사용자 승인 후 착수)
- **T3.1** `design/effects.py` — Effect 어휘 6종(RECOMMEND/REQUIRE/REQUIRE_ALARM/
  REQUIRE_INTERLOCK/REVIEW/GENERATE_TEST) → DesignDecision 매핑. 안전 성격 효과는
  최소 위험도 HIGH로 승격(Human Approval 유도)
- **T3.2** `design/rule_engine.py` — `match_rules`(조건 매칭) + `apply_rules`
  (효과 실행). 조건이 참조한 활성 Fact + 규칙 + 지식을 결정에 연결(Traceability).
  재실행 idempotent(이전 미확정 결정 SUPERSEDED)
- **T3.3** Hard/Recommendation 구분 — Hard 결과 override_allowed=False,
  `override_decision`이 Hard 무시 시도를 409로 거부
- **T3.4** Conflict Detection — 동일 (subject_type, subject_id)에 상이한 값 지정 시 충돌 보고
- **T3.5** `design/rules_seed.py` + `load_rules` — PRD §12 예시 규칙(증기→Radar) 등 3종.
  ⚠️ Safety 효과 포함 규칙은 전문가 검토 대상(D6)
- **T3.6** `knowledge/knowledge_seed.py` + `load_knowledge` — §27 지식 35건
  (Industry 5/Process 10/Device 10/Sensor 10)
- **T3.7** `POST /api/projects/{id}/apply-rules/` + `POST /design-decisions/{id}/override/`

### 검증 결과 (컨테이너 내 실측)
- pytest **78 passed**, ruff clean, 마이그레이션 drift 없음
- 라이브 §12 end-to-end: 증기+연속레벨 Fact 3종 입력 → RULE-LEVEL-RADAR-STEAM 매칭 →
  결정 8건 생성(각 근거 Fact3+규칙1+지식1). 알람2·오버플로리뷰는 risk=HIGH·승인필요=True로
  승격. Hard Rule override 시도가 409 hard_rule_override_forbidden으로 거부됨
- load_knowledge 35건 / load_rules 3건 idempotent 로드 확인

### ⚠️ 사용자 검토 요청 (D6, PRD §33-15)
- Safety 효과를 포함한 규칙(RULE-LEVEL-RADAR-STEAM의 알람/오버플로, RULE-ESTOP-SAFETY-IO)은
  전문가 검토 후 확정 필요. `backend/apps/design/rules_seed.py` 참조

### 다음 단계
- 사용자 승인 후 Phase 4 (Design Engine) 착수

## 2026-07-07 — Phase 4-A: Design Engine (Sensor · I/O · PLC Sizing)
- **T4A.1** `sensors` 앱 — SensorRequirement(§14 파이프라인 필드) + SensorCandidate.
  `design_rules.select_sensor_profile`로 측정항목+환경(증기/부식/위생/CIP)→원리 결정론적 선정.
  근거는 decision FK로 단일화(Fact+지식 연결)
- **T4A.2** `io_points` 앱 — IOPoint(DI/DO/AI/AO). 설비별 표준 I/O 프로파일 + 센서 신호 →
  I/O 산출, 태그 유일성 보장, 수량 집계
- **T4A.3** `plc_design` 앱 — PLCSizingResult(§15 요소: PID/Safety/이중화/확장여유/기존벤더) +
  PLCCandidate. 등급 판정 + Rejected Candidates and Reasons
- **T4A.4** `design/orchestrator.generate_design` + `POST /projects/{id}/generate-design/`
  (stage=sensor|io|plc|all), 재실행 idempotent. 산출물 읽기 API 3종
- 산출물은 decision FK로 원 Fact/규칙/지식까지 역추적 가능(Traceability 체인)

### 검증 결과 (컨테이너 내 실측)
- pytest **94 passed**, ruff clean, 마이그레이션 drift 없음
- 라이브 end-to-end(식품 CIP 탱크): 센서 LEVEL→RADAR(증기)·TEMP→RTD, 둘 다 IP69K+위생 반영 →
  I/O DI6/DO3/AI3/AO1(13점) → PLC MODULAR(Safety I/O 반영), LS ELECTRIC 채택·
  Siemens/Mitsubishi 탈락사유 명시
- Traceability 체인 테스트: 센서 유래 I/O → SensorRequirement → DesignDecision → 입력 Fact 역추적

### 다음 단계
- 사용자 승인 후 Phase 4-B (Communication · HMI) 착수

## 2026-07-07 — Phase 4-B: Design Engine (Communication · HMI)
- **T4B.1** `communications` 앱 — CommNode/CommLink/ProtocolRequirement. CONTROL_MODE/
  HMI/COMM_TARGETS/SCADA/MES/원격 Fact → 노드·링크·요구 생성. 네트워크 세그먼트
  4종, 인버터/서보 링크는 통신 두절 시 SAFE_STATE, SCADA→OPC UA, MES→게이트웨이+MQTT
- **T4B.2** `hmi_design` 앱 — HMIScreen/HMITag. 기본 7화면 + 조건부 화면
  (AUTO_SEQUENCE/TREND/RECIPE/IO_MONITOR/INTERLOCK_STATUS/COMM_STATUS/REPORT/MAINTENANCE)만
  생성. 화면별 보안등급, I/O Monitor는 IOPoint에서 태그 파생
- **T4B.3** orchestrator STAGE_ORDER 확장(sensor→io→plc→comm→hmi), 읽기 API 4종
- 산출물은 decision FK로 Traceability 확보

### 검증 결과 (컨테이너 내 실측)
- pytest **104 passed**, ruff clean, 마이그레이션 drift 없음
- 라이브 end-to-end(식품 라인): 통신 노드 6·링크 5(인버터 SAFE_STATE, SCADA OPC UA,
  MES 게이트웨이+MQTT) + 프로토콜 요구 3종(GATEWAY/MQTT/OPC_UA), HMI 조건부 13화면 생성
- 조건부 화면 테스트: RECIPE_REQUIRED 없음→미생성, 설정 시 생성

### 다음 단계
- 사용자 승인 후 Phase 4-C (Alarm · Interlock · Sequence · FAT/SAT) 착수

## 2026-07-07 — Phase 4-C: Design Engine (Alarm · Interlock · Sequence · FAT/SAT)
- **T4C.1** `alarms` 앱 — Alarm(§18 전체 필드). ALARM_REQUIREMENT 결정 + 통신 링크 →
  구조화 알람 materialize
- **T4C.2** `interlocks` 앱 — Interlock(§18). INTERLOCK_REQUIREMENT 결정 → materialize,
  Safety 인터록은 safety_related + bypass 권한 정책 필수. **Cause & Effect Matrix** selector
- **T4C.3** `sequences` 앱 — Sequence/SequenceStep(§19). CONTROL_MODE AUTO/SEMI →
  Vendor Independent 3단계(준비-운전-정지) 초안, 타임아웃·abort·hold/resume 포함
- **T4C.4** `fat_sat` 앱 — TestCase(§24). 센서·알람·인터록·시퀀스 → FAT/SAT 테스트 자동
  생성, source_type/source_ref로 원 산출물 역추적, 실행 결과 기록 API
- **T4C.5** orchestrator STAGE_ORDER 완성(sensor→io→plc→comm→hmi→alarm→sequence→test),
  C&E 매트릭스 엔드포인트, 읽기 API 4종
- **→ Phase 4 (Design Engine) 완성: PRD §13의 13종 산출물 전부 생성**

### 검증 결과 (컨테이너 내 실측)
- pytest **114 passed**, ruff clean, 마이그레이션 drift 없음
- 라이브 end-to-end(식품 CIP 탱크): apply-rules → generate-design(all) →
  센서2·I/O10·PLC(MODULAR)·통신·HMI10·알람·인터록(ESTOP)·시퀀스(3스텝)·FAT7/SAT4 생성
- Cause & Effect Matrix 도출, FAT/SAT가 ALARM/INTERLOCK/SENSOR/SEQUENCE로 역추적됨
- Safety 인터록(ESTOP) bypass 권한 정책 확인

### 다음 단계
- 사용자 승인 후 Phase 5 (Validation & Approval) 착수
