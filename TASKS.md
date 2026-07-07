# TASKS.md — Phase 4-A: Design Engine (Sensor · I/O · PLC Sizing)

**목표:** 규칙이 만든 요구/추천과 ProjectFact를 실제 설계 산출물로 구체화한다.
각 산출물은 DesignDecision(Traceability)로 근거를 남긴다. (이전 내역은 WORKLOG.md 참조)

**설계 원칙:** 도메인 산출물(SensorRequirement 등)은 구조화된 상세를 담고,
근거·추적은 `decision = FK(DesignDecision)`로 단일화한다. Design Engine 서비스가
`create_design_decision`으로 결정을 남긴 뒤 산출물을 생성한다.

## T4A.1 sensors 앱 — Sensor Design (§14 파이프라인)
- `SensorRequirement`: measurement_type → principle → technology → signal_type →
  accuracy → range → response_time → material_compat → env_rating →
  install_constraints → maintenance → comm_requirements (+ decision FK)
- `SensorCandidate`: vendor/model/rationale + rejected/reject_reason
- `services.generate_sensor_requirements(project)` — MEASUREMENT_REQUIREMENTS Fact +
  환경 Fact(STEAM/부식/위생 등) 기반 결정론적 원리 선정, 지식 후보 연결
- ✓ 증기+연속레벨 → RADAR/4-20mA·HART, 근거 추적 테스트

## T4A.2 io_points 앱 — I/O Estimation
- `IOPoint`: tag, signal_type(DI/DO/AI/AO), description, device/sensor 참조, decision FK
- `services.estimate_io(project)` — DEVICE_LIST + 센서요구 → I/O 생성 + 수량 집계
- 중복 태그 방지, 여유율 별도(PLC Sizing에서 반영)
- ✓ 설비/센서 → DI/DO/AI/AO 수량 산출 테스트

## T4A.3 plc_design 앱 — PLC Sizing (§15)
- `PLCSizingResult`: DI/DO/AI/AO 수량 + §15 요소(고속카운터/모션/PID/Safety/이중화/
  확장여유/기존벤더 등) + required_class + min_spec_json + selection_reason
- `PLCCandidate`: vendor/family + accepted + reason (Rejected Candidates and Reasons 포함)
- `services.size_plc(project)` — I/O 집계 + 여유율 + Fact 반영 → 등급·후보 산출
- ✓ I/O 수량·기존벤더 Fact → 등급/후보/탈락사유 테스트

## T4A.4 오케스트레이션 API
- `POST /api/projects/{id}/generate-design/?stage=sensor|io|plc|all` (4-A 범위: sensor/io/plc)
- 재실행 idempotent(이전 산출물 대체), 결과 요약 반환
- ✓ end-to-end: 인터뷰 상태 → apply-rules → generate-design → 산출물 + Traceability

## Phase 4-A Exit Checklist
- [ ] 전체 pytest green, ruff clean, 마이그레이션 drift 없음
- [ ] 센서→I/O→PLC 체인이 근거(Fact/규칙/지식)까지 역추적 가능
- [ ] PLC Sizing 출력에 Rejected Candidates and Reasons 포함
- [ ] WORKLOG.md 갱신 + 사용자 승인 → Phase 4-B
