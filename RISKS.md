# RISKS.md — 주요 기술 리스크와 대응방안

| # | 리스크 | 영향 | 발생가능성 | 대응방안 |
|---|---|---|---|---|
| R1 | **도메인 데이터 저작 병목** — 질문 50~300개, 지식항목, 규칙은 코드가 아니라 자동화 전문가의 지식 저작물. 엔진이 완성돼도 데이터가 없으면 제품이 비어 보임 | 높음 | 높음 | Phase 2부터 데이터 저작을 코드와 병행. 식품/수처리 2개 업종에 집중해 깊이 우선. 질문/규칙을 fixture(JSON)로 관리해 전문가가 코드 없이 기여 가능하게 함 |
| R2 | **conditions_json 표현력 부족/과잉** — 선언형 규칙 문법이 너무 약하면 규칙을 못 쓰고, 너무 강하면 사실상 코드가 되어 검증 불가 | 높음 | 중간 | JSONLogic 계열의 제한된 문법으로 시작. 문법으로 표현 불가한 규칙은 명시적 Python Rule 클래스로 화이트리스트 등록. Phase 3에서 §12 예시 규칙으로 표현력 검증 |
| R3 | **질문 점수 가중치 콜드스타트** — §8.5 점수 요소의 가중치 근거 데이터 없음 | 중간 | 높음 | 초기엔 단순 가중치 + criticality 우선. QuestionSelectionLog를 처음부터 기록해 추후 튜닝 근거 확보. KPI(§28)로 Unnecessary Question Rate 측정 |
| R4 | **Safety 설계의 법적/안전 책임** — 자동 생성된 Interlock/Alarm이 틀리면 인명/설비 사고 가능 | 치명적 | 낮음 | Hard Rule은 Deterministic 코드로만, LLM 판단 금지(PRD §3.3). Safety 항목은 Human Approval 필수 + CRITICAL Finding 시 생성 차단. 산출물에 "엔지니어 검토 필수" 명시 |
| R5 | **LLM 의존 기능의 비용/가용성/일관성** — 답변 구조화 품질이 LLM에 좌우됨 | 중간 | 중간 | LLM Interface 추상화 + Rule-based fallback(정규식/단위 파서) 필수(PRD §33-13). LLM 출력은 항상 PROPOSED 상태로 저장하고 confidence 부여, 사용자 확인 후 CONFIRMED |
| R6 | **Traceability 그래프의 복잡도** — Fact→Decision→…→Test 체인이 M2M 다층이라 쿼리/무결성 관리가 어려움 | 중간 | 중간 | JSON ID 배열 대신 명시적 조인 테이블 사용. Traceability 조회는 selector 함수로 캡슐화하고 커버리지 검사를 Validation Engine 항목으로 자동화 |
| R7 | **ProjectState Projection 정합성** — Fact 변경/모순/폐기 시 Projection 재계산 누락 | 중간 | 중간 | Projection은 저장 대신 온디맨드 계산으로 시작(MVP 규모에서 충분). 성능 문제 확인 후에만 materialize. FactStatus 상태기계 전이를 서비스 계층 한 곳으로 강제 |
| R8 | **Vendor Adapter 실현 가능성** — 제조사 파일 포맷은 비공개/바이너리가 많음 | 중간 | 높음 | MVP에서 제외 확정(PRD §26). Phase 7은 ST/CSV 텍스트 출력까지만. IR 스키마를 먼저 고정해 어댑터 교체 가능 구조 유지 |
| R9 | **범위 팽창(Scope Creep)** — PRD가 넓어 MVP가 늘어질 위험 | 높음 | 높음 | Phase Gate + 사용자 승인 포인트(PRD §33-24) 엄수. 각 Phase Exit 기준을 ACCEPTANCE_CRITERIA.md로 고정 |
| R10 | **단위/한글 처리 오류** — 80℃/80도/176℉ 등 단위 변환, 한글 인코딩 깨짐 | 중간 | 중간 | pint 등 단위 라이브러리로 Unit Conversion 단계 구현, UNIT_VALUE 질문 유형에 단위 스키마 강제. UTF-8 왕복 테스트를 Phase 0부터 CI에 포함 |
| R11 | **22개 앱 간 순환 의존** — 도메인이 서로 얽혀 import 순환 발생 가능 | 중간 | 중간 | PLAN.md §3.2 의존 방향 규칙 준수, import-linter로 CI에서 강제 |
| R12 | **감사로그 누락** — 서비스 계층을 우회한 변경(admin, shell)이 audit에 안 남음 | 낮음 | 중간 | 감사 대상 쓰기 작업을 service 함수로만 허용하는 컨벤션 + 핵심 모델에 대한 변경 감지 테스트 |
