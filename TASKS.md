# TASKS.md — Phase 4-B: Design Engine (Communication · HMI)

**목표:** 규칙 결과와 설계 상태로 통신 구성(§16)과 HMI 화면 구조(§17)를 생성한다.
각 산출물은 DesignDecision(Traceability)로 근거를 남긴다. (이전 내역은 WORKLOG.md 참조)

## T4B.1 communications 앱 — Communication Design (§16)
- `CommNode`: PLC/HMI/Remote I/O/Inverter/SCADA/Gateway/MES 노드
- `CommLink`: 노드 간 링크(프로토콜, 네트워크 세그먼트, 매체, 장애거동)
- `ProtocolRequirement`: OPC UA/MQTT/게이트웨이/시간동기 요구
- `services.generate_communication(project)` — CONTROL_MODE/HMI_REQUIRED/COMM_TARGETS/
  SCADA/MES/원격모니터링 Fact + 인버터통신 결정 → 노드·링크·요구 생성
- Device Communication Matrix, Protocol Compatibility, Failure Behavior, 통신 알람 반영
- ✓ 인버터→필드버스 링크, HMI 링크, SCADA/OPC UA 요구 테스트

## T4B.2 hmi_design 앱 — HMI Design (§17)
- `HMIScreen`: name/purpose/user_role/security_level + required_tags/commands/
  status/alarm/trend objects + navigation
- `HMITag`: 태그명/신호/소스(IOPoint/Alarm) 연결
- `services.generate_hmi(project)` — 설계 상태 조건별로 **필요한 화면만** 생성
  (기본 세트 + Trend는 TREND_REQUIRED, Recipe는 RECIPE_REQUIRED,
  Interlock/Alarm은 Safety 요구, I/O Monitor는 I/O 존재 시 등)
- HMI 태그는 IOPoint에서 파생
- ✓ 조건부 화면 생성 테스트(Recipe 없음→미생성, 있음→생성)

## T4B.3 오케스트레이션 확장
- STAGE_ORDER에 comm, hmi 추가 (sensor→io→plc→comm→hmi)
- 읽기 API: comm-nodes/comm-links/hmi-screens
- ✓ generate-design?stage=all end-to-end

## Phase 4-B Exit Checklist
- [ ] 전체 pytest green, ruff clean, 마이그레이션 drift 없음
- [ ] 필요한 HMI 화면만 조건부 생성됨
- [ ] 통신 구성이 근거(Fact/결정)까지 역추적 가능
- [ ] WORKLOG.md 갱신 + 사용자 승인 → Phase 4-C
