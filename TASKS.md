# TASKS.md — Phase 4-C: Design Engine (Alarm · Interlock · Sequence · FAT/SAT)

**목표:** 규칙이 만든 알람/인터록 요구를 구조화하고, 시퀀스와 FAT/SAT 테스트를 생성한다.
Phase 4(Design Engine) 완성. (이전 내역은 WORKLOG.md 참조)

## T4C.1 alarms 앱 — Alarm (§18)
- `Alarm`: code/source/condition/delay/priority/message/operator_action/reset_type/
  latching/related_interlock/fat_test_required/sat_test_required (+ decision FK)
- ALARM_REQUIREMENT 결정 + CRITICAL_ALARMS Fact → 구조화 Alarm
- ✓ 알람 생성·근거 추적 테스트

## T4C.2 interlocks 앱 — Interlock (§18) + Cause & Effect
- `Interlock`: code/protected_device/condition/effect/reset_condition/bypass_allowed/
  bypass_permission/safety_related/reason/fat_test_required/sat_test_required
- INTERLOCK_REQUIREMENT 결정 + ESTOP/INTERLOCK_REQUIREMENTS Fact → 구조화 Interlock
- Cause & Effect Matrix selector(알람+인터록 기반)
- ✓ 인터록 생성, safety_related 시 bypass 권한 필수, C&E 매트릭스 테스트

## T4C.3 sequences 앱 — Sequence (§19)
- `Sequence` + `SequenceStep`: entry_condition/actions/completion_condition/timeout/
  timeout_alarm/abort_condition/hold_condition/resume_condition/next_step/fallback_step
- CONTROL_MODE AUTO/SEMI + SEQUENCE_OUTLINE → Vendor Independent 시퀀스 초안
- ✓ 시퀀스 스텝 생성, 타임아웃 알람 연계 테스트

## T4C.4 fat_sat 앱 — FAT/SAT Test (§24)
- `FatTestCase`/`SatTestCase`: test_id/category/precondition/procedure/expected_result/
  actual_result/status/evidence/tester/reviewer + source 역추적
- 요구·센서·알람·인터록·시퀀스 → 테스트 자동 생성 (알람 시뮬, 인터록 트립, 센서 검증 등)
- ✓ 커버리지: 각 알람/인터록이 FAT/SAT 테스트로 커버됨, 원 요구 역추적

## T4C.5 오케스트레이션 확장
- STAGE_ORDER: ...→alarm→sequence→test, 읽기 API + C&E 매트릭스 엔드포인트
- ✓ generate-design?stage=all end-to-end (전체 13종 산출물)

## Phase 4-C Exit Checklist
- [ ] 전체 pytest green, ruff clean, 마이그레이션 drift 없음
- [ ] Cause & Effect Matrix가 알람+인터록에서 도출됨
- [ ] FAT/SAT가 알람·인터록·시퀀스로부터 생성되고 원 요구로 역추적됨
- [ ] Safety 인터록은 bypass 권한/기록 정책 포함
- [ ] WORKLOG.md 갱신 + 사용자 승인 → Phase 5 (Validation & Approval)
