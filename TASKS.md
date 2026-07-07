# TASKS.md — Phase 3: Knowledge & Rule Engine

**목표:** 선언형 규칙(conditions_json)을 프로젝트 상태에 매칭하고, 효과(effects_json)를
Traceability 있는 DesignDecision으로 실행한다. Hard/Recommendation을 구분하고 충돌을
탐지한다. §27 초기 지식 데이터를 적재한다.
(이전 Phase 내역은 WORKLOG.md 참조)

## T3.1 Effect 어휘 + Executor (`design/effects.py`)
- effect 유형: RECOMMEND, REQUIRE, REQUIRE_ALARM, REQUIRE_INTERLOCK, REVIEW, GENERATE_TEST
- 각 effect → DesignDecision(decision_type, subject_type, value, risk_level) 매핑
- 알 수 없는 effect 유형은 DomainError
- ✓ 유형별 실행 테스트

## T3.2 Rule Matcher + Engine (`design/rule_engine.py`)
- `match_rules(state)` — is_active 규칙 중 conditions_json이 참인 것, priority 정렬
- `apply_rules(project, actor)` — 매칭 규칙의 effects를 실행해 DesignDecision 생성
  (입력 Fact = 조건에서 참조된 활성 Fact, rule/knowledge 연결로 Traceability 확보)
- 재실행 시 규칙당 기존 Decision을 SUPERSEDED 처리(idempotent, 파괴적 갱신 금지)
- ✓ 매칭/미매칭 테스트, 재실행 idempotency 테스트

## T3.3 Hard Rule / Recommendation 구분
- Hard Rule 효과는 override_allowed=False로 표기, 사용자 무시 시도 시 거부
- Recommendation은 override 가능(+AuditEvent 기록)
- ✓ Hard override 거부 / Recommendation override 허용 테스트

## T3.4 Conflict Detection
- 동일 (subject_type, subject_id)에 서로 다른 값을 지정하는 규칙 → 충돌 기록
- Hard vs Recommendation 충돌 시 Hard 우선, 양쪽 근거 보존
- ✓ 충돌 탐지 테스트

## T3.5 §12 예시 규칙 시드 (`design/rules_seed.py` + `load_rules`)
- 증기 환경 탱크 연속 레벨 → Radar + AI + High/Low Alarm + Overflow Review + HMI Trend
  + FAT/SAT Test (8개 효과)
- ⚠️ Safety 관련(Alarm/Interlock/Overflow) 규칙은 전문가 검토 대상(D6)
- ✓ 규칙 적용 시 8개 효과 전부 DesignDecision 생성 + 근거 연결 검증

## T3.6 §27 초기 지식 데이터 (`knowledge/knowledge_seed.py` + `load_knowledge`)
- Industry 5, Process 10, Device 10, Sensor 10 (KnowledgeItem)
- ✓ 로드 + idempotent 테스트

## T3.7 API — 규칙 적용
- `POST /api/projects/{id}/apply-rules/` → 생성된 DesignDecision + 충돌 리포트
- 규칙이 참조한 지식 항목을 Decision에 연결
- ✓ API 테스트 (§12 시나리오 end-to-end)

## Phase 3 Exit Checklist
- [ ] 전체 pytest green, ruff clean, 마이그레이션 drift 없음
- [ ] §12 예시 규칙의 8개 효과가 근거와 함께 DesignDecision으로 기록됨
- [ ] Hard Rule override 거부 동작
- [ ] 규칙/지식 버전 변경 시 기존 Decision SUPERSEDED
- [ ] §27 지식 데이터 로드 가능
- [ ] WORKLOG.md 갱신 + 사용자 승인 (Safety 규칙 검토 요청)
