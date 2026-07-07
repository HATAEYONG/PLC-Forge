# TASKS.md — Phase 7: LS ELECTRIC Adapter PoC (마지막)

**목표:** Vendor Independent IR(§20)을 만들고, LS ELECTRIC Adapter(§21)로 ST + CSV +
Vendor Mapping Report를 생성한다. CRITICAL Finding 시 생성 차단(§22). (이전 내역은 WORKLOG.md)

## T7.1 Vendor Independent IR (§20)
- `generators/ir.py` — build_ir(project): ProjectMetadata/DeviceDefinitions/SignalDefinitions/
  DataTypes/Alarms/Interlocks/Sequences/HMITags/TestRequirements/LogicExpressions
- IR_SCHEMA(JSON Schema) + validate_ir()
- §20 연산(ADD~CONTROL_FLOW) 표현 가능
- ✓ IR 빌드/스키마 검증 테스트

## T7.2 Adapter 인터페이스 (§21)
- `adapters/base.py` — VendorAdapter ABC: validate_ir/map_data_types/map_addresses/
  map_instructions/generate_program_structure/generate_tags/generate_alarm_mapping/
  generate_hmi_tags/generate_test_artifacts/package_output
- ✓ ABC 계약 테스트

## T7.3 LS ELECTRIC Adapter
- `adapters/ls_electric.py` — XGB 주소 매핑(%IX/%QX/%IW/%QW), BOOL/INT/REAL 데이터타입,
  ST 프로그램 구조(알람 검출 + 인터록 로직), Tag/IO/Alarm/HMI Tag CSV, Mapping Report
- ✓ 주소/데이터타입 매핑, ST 생성, CSV 생성 테스트

## T7.4 생성 서비스 + API (CRITICAL 차단)
- `services.generate_vendor_package(project, vendor)` — assert_generation_allowed 게이트
- `POST /api/projects/{id}/vendor-generate/?vendor=ls` → 파일 묶음 + report
- validate_ir 실패 시 생성 중단
- ✓ CRITICAL 차단 테스트, end-to-end 생성 테스트

## Phase 7 Exit Checklist
- [ ] 전체 pytest green, ruff clean, 마이그레이션 drift 없음
- [ ] IR 스키마 검증 + LS ST/CSV/Report 생성
- [ ] CRITICAL Finding 시 어댑터 실행 차단
- [ ] WORKLOG.md 갱신 — PRD Phase 0~7 전체 완성 보고
