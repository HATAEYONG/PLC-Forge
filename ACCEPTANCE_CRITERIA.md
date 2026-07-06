# ACCEPTANCE_CRITERIA.md

각 Phase의 완료 판정 기준. 모든 기준은 자동 테스트 또는 재현 가능한 절차로 검증한다.
"실패한 테스트를 삭제하거나 우회하지 않는다"(PRD §33-6)를 전 Phase에 적용한다.

---

## Phase 0 — Repository Bootstrap
- [ ] 신규 클론 후 README 절차만으로 `docker compose up` → backend `/api/health/` 200 (DB 연결 포함)
- [ ] frontend 개발 서버 기동 및 health 상태 표시
- [ ] backend: pytest green, ruff clean / frontend: vitest green, eslint clean
- [ ] API 오류 응답이 통일 포맷 `{"error": {code, message, details}}` 을 따름 (테스트 3건+)
- [ ] 한글 문자열 저장→조회 왕복 테스트 통과
- [ ] GitHub Actions CI가 PR에서 위 검사를 수행

## Phase 1 — Core Domain
- [ ] Company/Project/Question/AnswerOption/InterviewSession/InterviewAnswer/ProjectFact/
      KnowledgeItem/Rule/DesignDecision CRUD API가 존재하고 각각 목록/생성/조회/수정 테스트 보유
- [ ] Question이 PRD §8.2 필드를 모두 가짐 (answer_schema는 JSON Schema 검증)
- [ ] ProjectFact가 §10 필드 + FactStatus 5상태를 가지며, 허용되지 않은 상태 전이가 거부됨
- [ ] DesignDecision 생성 시 input_fact/rule/knowledge 연결 없이 저장 불가(Traceability 강제)
- [ ] 마이그레이션이 빈 DB에서 오류 없이 재적용 가능
- [ ] 모든 쓰기 로직이 services.py에 위치(ViewSet/Serializer에 비즈니스 로직 없음 — 코드리뷰 체크)

## Phase 2 — Question Engine
- [ ] required/exclusion/applicable 조건으로 후보가 올바르게 필터링됨 (경계 테스트 포함)
- [ ] §8.5의 각 점수 요소가 개별 단위 테스트를 가짐
- [ ] 질문 선택 시 QuestionSelectionLog에 점수 내역과 선택 이유가 저장됨
- [ ] §8.6 종료조건: 하나라도 미충족이면 INTERVIEW_COMPLETE를 반환하지 않음
- [ ] 시나리오 테스트: "탱크 3개, 2개는 80도, 세척 시 증기" 답변 →
      TANK_COUNT=3, HEATED_TANK_COUNT=2, MAX_TEMPERATURE_APPROX=80C,
      STEAM_PRESENT_DURING_CIP=TRUE, CIP_REQUIRED=TRUE Fact 생성 (LLM 미사용 경로)
- [ ] 동일 fact_key에 모순 값 입력 시 CONFLICTED 상태 + Conflict Resolution 질문 점수 상승
- [ ] 초기 질문 데이터 50개 fixture 로드 및 스키마 검증 통과

## Phase 3 — Knowledge & Rule Engine
- [ ] §12 예시(Radar Level) 규칙이 fixture로 존재하고, 조건 충족 시 8개 효과가 모두 실행됨
- [ ] Hard Rule은 사용자 무시 시도 시 거부되고, Recommendation Rule은 override 가능(+기록)
- [ ] 규칙 적용 결과가 DesignDecision에 rule_ids/knowledge_item_ids/explanation과 함께 저장
- [ ] 규칙 버전 변경 시 기존 Decision은 SUPERSEDED 처리(파괴적 갱신 금지)
- [ ] §27 초기 지식 데이터(업종 5, 공정 10, 설비 10, 센서 10) 로드 통과

## Phase 4 — Design Engine
- [ ] 센서 설계가 §14 순서(원리→기술→신호→…→후보)를 따르며 각 단계 근거 저장
- [ ] I/O Estimation이 Device/Sensor로부터 DI/DO/AI/AO 수량을 산출하고 여유율 반영
- [ ] PLC Sizing이 §15 입력요소를 반영하고 출력에 Rejected Candidates and Reasons 포함
- [ ] HMI 화면이 답변/설계 상태 조건에 따라 필요한 화면만 생성됨
- [ ] Alarm/Interlock에서 Cause & Effect Matrix 도출 가능
- [ ] FAT/SAT Draft가 Alarm/Interlock/Sequence로부터 자동 생성되고 원 요구사항으로 역추적 가능
- [ ] Traceability 체인 테스트: 임의 FatTestCase → Requirement까지 selector로 역추적 성공

## Phase 5 — Validation & Approval
- [ ] §22의 각 검사 항목이 최소 1개의 양성/음성 테스트를 가짐
- [ ] **CRITICAL Finding 존재 시 Vendor Generation API가 403/409로 차단됨** (핵심 테스트)
- [ ] Approval 상태기계(DRAFT→IN_REVIEW→APPROVED/REJECTED, SUPERSEDED)가 강제되고
      건너뛰기 전이가 거부됨
- [ ] Safety 관련 대상(§3.5)은 승인 없이 CONFIRMED 될 수 없음
- [ ] 모든 승인/거절이 AuditEvent에 actor/before/after/reason과 함께 기록됨

## Phase 6 — Frontend
- [ ] Playwright E2E: 로그인 → 프로젝트 생성 → 인터뷰(질문 5개 이상 응답) →
      설계 생성 → Validation 확인 → 승인 → Excel Export 다운로드 해피패스 통과
- [ ] 인터뷰 화면이 질문 유형 12종(§8.3)별 입력 위젯을 제공
- [ ] Project State 화면에 Fact 목록/상태/출처 답변 링크 표시
- [ ] Design Preview에서 각 Decision의 근거(입력 답변, 규칙, 지식, 신뢰도) 열람 가능
- [ ] 한글 UI/데이터가 전 화면에서 깨지지 않음

## Phase 7 — LS ELECTRIC Adapter PoC
- [ ] Vendor Independent IR이 §20 구성요소와 §20 연산(ADD~CONTROL_FLOW)을 표현 가능하고
      JSON Schema 검증기를 가짐
- [ ] 샘플 프로젝트에서 ST 코드 + Tag/IO/Alarm/HMI Tag CSV + Vendor Mapping Report 생성
- [ ] validate_ir() 실패 시 생성이 중단되고 원인 리포트 제공
- [ ] CRITICAL ValidationFinding이 있는 프로젝트는 어댑터 실행 자체가 차단됨

## MVP 전체 (릴리스 판정)
- [ ] PRD §26 MVP 26개 항목이 각각 동작 데모 가능
- [ ] §31 필수 테스트 14종이 모두 존재하고 green
- [ ] MVP 제외 항목(§26)이 코드베이스에 미포함(범위 준수)
