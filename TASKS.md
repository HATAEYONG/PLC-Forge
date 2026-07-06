# TASKS.md — Phase 2: Question Engine

**목표:** 적응형 질문 선택(필터링→점수화→선택→종료조건)과 Rule-based Answer Processing
파이프라인을 구현한다. LLM 없이 동작해야 한다 (PRD §33-13).
(이전 Phase 내역은 WORKLOG.md 참조)

## T2.1 JSONLogic 조건 평가기 (D4 확정)
- `core/jsonlogic.py` — var, ==, !=, >, >=, <, <=, and, or, not(!), in, missing 지원
- Question.required_conditions / exclusion_conditions / Rule.conditions_json 공용
- ✓ 연산자별 단위 테스트

## T2.2 질문 후보 필터링
- is_active + 미답변 + required_conditions 충족 + exclusion_conditions 불충족
- applicable_industries / applicable_processes (프로젝트 Fact의 INDUSTRY/PROCESS와 대조,
  미확정 시 통과)
- ✓ 조건별 포함/제외 테스트

## T2.3 질문 점수화 (§8.5)
- Base Priority + Missing Critical Fact + Safety Risk + Information Gain
  + Design Unlock + Conflict Resolution + Downstream Impact
  − Redundancy − Already Answered − Not Applicable − User Fatigue
- 가중치는 상수 모듈에 정의 (콜드스타트: R3 대응 — SelectionLog로 추후 튜닝)
- ✓ 각 점수 요소 단위 테스트

## T2.4 다음 질문 선택 + 선택 이유 기록
- `QuestionSelectionLog` (session, question, total_score, score_breakdown, reason)
- `GET /api/interview/sessions/{id}/next-question/`
- ✓ 최고점 질문 반환 + 로그 저장 테스트

## T2.5 인터뷰 종료조건 (§8.6)
- Critical/Safety 커버리지, 주요 Fact 확보, 미해결 CONFLICTED 없음 등 10개 기준의
  MVP 구현 + 기준별 충족 리포트
- 미충족 시 계속 질문, 충족 시 next-question이 완료 응답 반환 + 세션 COMPLETED
- ✓ 기준별 충족/미충족 테스트

## T2.6 Answer Processing 파이프라인 (§9, Rule-based)
- Validation(answer_schema) → Normalization → Unit Conversion(온도 등 최소 단위계)
  → Entity Extraction(한국어 정규식 추출기) → Fact Generation(confidence 부여)
  → Contradiction Detection(기존 CONFIRMED와 상충 시 양쪽 CONFLICTED) → Projection
- 구조화 유형(INTEGER/YES_NO/UNIT_VALUE 등)은 unlocks_facts로 직접 매핑
- ✓ 시나리오: "탱크가 3개 있고 그중 두 개는 80도 정도이며 세척할 때 증기가 생깁니다"
  → TANK_COUNT=3, HEATED_TANK_COUNT=2, MAX_TEMPERATURE_APPROX=80C,
  STEAM_PRESENT_DURING_CIP=TRUE, CIP_REQUIRED=TRUE
- ✓ 모순 입력 → CONFLICTED + Conflict Resolution 질문 점수 상승 테스트

## T2.7 세션 API 확장 (§29)
- `/facts/`, `/state/`(Projection), `/progress/`(답변 수·커버리지 리포트)
- 답변 제출 응답에 생성된 Fact 목록 포함
- ✓ API 테스트

## T2.8 초기 질문 데이터 50개 (D5: 식품+수처리 우선, D6: 초안→사용자 검토)
- `load_questions` 관리 명령 + 데이터 모듈 (code 기준 idempotent upsert)
- ✓ 50개 로드, 스키마/중복 검증 테스트

## Phase 2 Exit Checklist
- [ ] 전체 pytest green, ruff clean, 마이그레이션 drift 없음
- [ ] 시나리오 테스트 통과 (LLM 미사용)
- [ ] 질문 50개 로드 가능
- [ ] WORKLOG.md 갱신 + 사용자 승인 (질문 데이터는 특히 Safety 항목 검토 요청)
