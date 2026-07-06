# PLC-Forge Product Requirements Document

**문서 버전:** v1.0  
**프로젝트 유형:** AI 기반 산업 자동화 자율설계 플랫폼  
**개발 환경:** Django + Django REST Framework + React(Vite) + PostgreSQL  
**주 개발 도구:** Claude Code  
**핵심 개발 원칙:** Vendor Independent First, Question Engine First, Evidence-Based Design, Human Approval Before Code Generation

---

# 1. 프로젝트 개요

## 1.1 제품명

PLC-Forge

## 1.2 제품 비전

PLC-Forge는 자동화 전문가가 고객과 현장 인터뷰를 수행하는 사고 과정을 소프트웨어로 구현하는 산업 자동화 자율설계 플랫폼이다.

사용자는 PLC, 센서, 산업통신, HMI에 대한 전문지식이 부족하더라도 컨설팅 방식의 적응형 질문에 답할 수 있다.

플랫폼은 답변을 구조화하고, 누락된 요구사항을 탐지하고, 추가 질문을 선택하고, 산업 지식베이스와 설계 규칙을 적용하여 다음 결과를 생성한다.

- 현장 요구사항 정의
- 공정 모델
- 설비 목록
- 센서 요구사항 및 추천 후보
- I/O List
- PLC 요구사양 및 후보
- 산업통신 구성
- HMI 화면 구조
- Alarm Matrix
- Interlock Matrix
- Cause & Effect Matrix
- Sequence Table
- FAT Test Case
- SAT Test Case
- PLC Vendor Independent Intermediate Representation
- 제조사별 PLC 프로젝트 생성용 입력 데이터
- 납품 문서

최종 목표는 다음과 같다.

```text
현장 인터뷰 → 요구사항 구조화 → 자율설계 → 설계 검증 → Human Approval → PLC/HMI/통신 설계 생성 → FAT/SAT → 납품문서
```

---

# 2. 핵심 문제 정의

기존 PLC 프로젝트는 다음 문제를 가진다.

1. 고객 요구사항이 비정형 대화, 엑셀, 도면, 메모에 분산된다.
2. 신규 업체는 필요한 센서와 데이터 수집 장치 자체를 모를 수 있다.
3. 자동화 엔지니어의 경험에 따라 질문 품질과 설계 품질이 크게 달라진다.
4. 센서, PLC, HMI, 통신, Alarm, Interlock, FAT/SAT 설계가 서로 분리되어 관리된다.
5. 특정 PLC 제조사 명령어부터 개발하면 재사용성과 이식성이 낮아진다.
6. 요구사항 변경 시 코드와 문서 간 추적성이 깨진다.
7. FAT/SAT 과정에서 설계 누락이 뒤늦게 발견된다.
8. 왜 특정 센서, 통신, PLC 또는 HMI 구조가 선정되었는지 근거가 남지 않는다.

PLC-Forge는 이러한 문제를 Question Engine, Knowledge Base, Rule Engine, Design Engine, Validation Engine, Vendor Adapter 구조로 해결한다.

---

# 3. 개발 원칙

## 3.1 Question Engine First

PLC 코드 생성기를 먼저 개발하지 않는다.

첫 번째 핵심 제품은 사용자의 답변에 따라 다음 질문을 선택하고 설계 상태를 갱신하는 Question Engine이다.

## 3.2 Vendor Independent First

Siemens, LS ELECTRIC, Mitsubishi 등의 제조사별 프로젝트를 직접 생성하기 전에 공통 설계 모델을 생성한다.

모든 설계 결과는 Vendor Independent Intermediate Representation을 거쳐야 한다.

## 3.3 Deterministic Core, AI Assisted

안전, 인터록, I/O 계산, 설계 필수조건, FAT/SAT 판정과 같은 핵심 로직은 가능한 한 명시적 규칙과 검증기로 구현한다.

LLM은 다음 영역에 우선 사용한다.

- 자연어 답변 구조화
- 모호성 탐지
- 추가 질문 후보 생성
- 문서 분석
- 설계 설명
- 누락 가능성 제안
- 설계 리뷰 보조

LLM 단독 판단으로 Safety Critical 설계를 확정하지 않는다.

## 3.4 Evidence-Based Design

모든 설계 결정에는 다음 정보가 남아야 한다.

- 결정 내용
- 결정 이유
- 입력 답변
- 적용 규칙
- 참조 지식
- 신뢰도
- 승인 상태
- 생성 버전

## 3.5 Human-in-the-Loop

다음 단계는 사용자 또는 엔지니어 승인 없이 자동 확정하지 않는다.

- Safety 관련 설계
- 센서 최종 모델 선정
- PLC 최종 모델 선정
- 통신망 최종 구성
- Interlock 해제 또는 Bypass
- Vendor Code Generation
- FAT 승인
- SAT 승인

## 3.6 Traceability First

다음 연결 관계를 추적할 수 있어야 한다.

```text
Requirement → Answer → Fact → Design Decision → Device → Sensor → I/O → Alarm → Interlock → Sequence → PLC Logic → HMI Object → FAT Test → SAT Test → Delivery Document
```

---

# 4. 핵심 사용자

## 4.1 자동화 컨설턴트

신규 고객과 인터뷰하고 자동화 범위를 정의한다.

## 4.2 PLC 엔지니어

확정된 설계 결과를 검토하고 제조사별 PLC 프로젝트를 생성한다.

## 4.3 전기설계 엔지니어

센서, 계측기, I/O, 판넬 및 네트워크 설계에 활용한다.

## 4.4 HMI/SCADA 엔지니어

화면, Alarm, Trend, Recipe, 권한, Historian 요구사항을 생성한다.

## 4.5 FAT/SAT 담당자

요구사항과 설계 결과를 기반으로 시험 항목을 생성하고 실행 결과를 기록한다.

## 4.6 프로젝트 관리자

설계 진행률, 미결정 사항, 위험요소, 승인 상태, 문서 완성도를 관리한다.

---

# 5. 전체 시스템 아키텍처

```text
User
  ↓
React Interview UI
  ↓
Django REST API
  ↓
Interview Orchestrator
  ↓
Answer Normalizer
  ↓
Project State Manager
  ↓
Question Engine
  ↓
Knowledge Retrieval Engine
  ↓
Rule Engine
  ↓
Design Engine
  ↓
Validation & Conflict Engine
  ↓
Design Review Queue
  ↓
Human Approval
  ↓
Vendor Independent IR
  ↓
Vendor Adapter
  ↓
PLC/HMI/Document Generator
  ↓
FAT/SAT
  ↓
As-Built Package
```

---

# 6. Backend 애플리케이션 구조

`backend/apps` 아래에 다음 Django App을 생성한다.

```text
accounts
companies
projects
interview
knowledge
requirements
processes
devices
sensors
io_points
communications
plc_design
hmi_design
alarms
interlocks
sequences
design
validation
approvals
generators
documents
fat_sat
audit
```

각 앱은 가능한 한 다음 구조를 사용한다.

```text
models.py
serializers.py
selectors.py
services.py
permissions.py
urls.py
views.py
tests/
```

비즈니스 로직을 ViewSet, Serializer, Model.save(), Django Signal에 집중시키지 않는다.

핵심 비즈니스 로직은 Service Layer에 구현한다.

---

# 7. Frontend 구조

```text
frontend/src

api/
components/
features/
hooks/
layouts/
pages/
routes/
stores/
types/
utils/
```

주요 Feature:

```text
auth
companies
projects
interview
project-state
design-review
devices
sensors
io-list
communications
plc-design
hmi-design
alarms
interlocks
sequences
fat-sat
documents
```

---

# 8. Question Engine 요구사항

## 8.1 목적

Question Engine은 고정 설문지가 아니다.

현재까지 확보된 정보와 설계 불확실성을 기반으로 다음 질문을 선택한다.

## 8.2 Question 데이터

Question은 최소 다음 필드를 가진다.

```text
id
code
version
text
help_text
category
question_type
answer_schema
priority
criticality
required_conditions
exclusion_conditions
applicable_industries
applicable_processes
unlocks_facts
unlocks_decisions
risk_detection_tags
is_active
created_at
updated_at
```

## 8.3 질문 유형

```text
TEXT
YES_NO
SINGLE_CHOICE
MULTI_CHOICE
INTEGER
DECIMAL
RANGE
UNIT_VALUE
DEVICE_LIST
TABLE
FILE_UPLOAD
CONFIRMATION
```

## 8.4 질문 카테고리

```text
COMPANY
INDUSTRY
PROCESS
PRODUCTION
DEVICE
MATERIAL
SENSOR
QUALITY
SAFETY
ENVIRONMENT
MAINTENANCE
NETWORK
COMMUNICATION
PLC
HMI
SCADA
HISTORIAN
MES_ERP
ALARM
INTERLOCK
SEQUENCE
FAT
SAT
DELIVERY
```

## 8.5 다음 질문 선정 기준

질문 점수는 최소 다음 요소를 고려한다.

```text
Base Priority
+ Missing Critical Fact Score
+ Safety Risk Score
+ Information Gain Score
+ Design Unlock Score
+ Conflict Resolution Score
+ Downstream Impact Score
- Redundancy Penalty
- Already Answered Penalty
- Not Applicable Penalty
- User Fatigue Penalty
```

Question Engine은 질문을 선택할 때 선택 이유를 저장한다.

## 8.6 질문 종료 조건

단순히 모든 질문을 완료했다고 종료하지 않는다.

다음 조건을 만족해야 한다.

- Critical Requirement Coverage 충족
- Safety Question Coverage 충족
- 주요 Device 식별 완료
- 주요 Sensor Requirement 식별 완료
- I/O Estimation 가능
- PLC Sizing 가능
- Communication Architecture 생성 가능
- HMI Minimum Screen Set 생성 가능
- Alarm/Interlock 초안 생성 가능
- 미해결 Critical Conflict 없음

종료되지 않은 경우 추가 질문을 수행한다.

---

# 9. Answer Processing 요구사항

사용자 답변을 곧바로 ProjectState 필드에 저장하지 않는다.

다음 파이프라인을 적용한다.

```text
Raw Answer
→ Validation
→ Normalization
→ Unit Conversion
→ Entity Extraction
→ Fact Generation
→ Confidence Assignment
→ Contradiction Detection
→ Project State Projection
```

예시:

사용자 답변:

```text
탱크가 3개 있고 그중 두 개는 80도 정도이며 세척할 때 증기가 생깁니다.
```

생성 Fact:

```text
TANK_COUNT = 3
HEATED_TANK_COUNT = 2
MAX_TEMPERATURE_APPROX = 80 C
STEAM_PRESENT_DURING_CIP = TRUE
CIP_REQUIRED = TRUE
```

원본 답변과 구조화 Fact 간 연결을 유지한다.

---

# 10. Project State 모델

ProjectState를 하나의 거대한 테이블로 만들지 않는다.

다음 구조를 사용한다.

## ProjectFact

```text
project
fact_key
value_json
value_type
unit
source_type
source_answer
confidence
status
version
created_at
```

## FactStatus

```text
PROPOSED
CONFIRMED
CONFLICTED
SUPERSEDED
REJECTED
```

ProjectState는 ProjectFact를 기반으로 계산되는 Projection 또는 Materialized Summary로 구현한다.

---

# 11. Knowledge Base 설계

지식베이스는 단순 문서 저장소가 아니다.

최소 다음 8개 계층으로 구성한다.

1. Industry Knowledge
2. Process Knowledge
3. Device Knowledge
4. Instrument/Sensor Knowledge
5. Control Knowledge
6. Communication Knowledge
7. HMI/SCADA Knowledge
8. FAT/SAT Knowledge

향후 다음 지식을 추가한다.

- Safety Standards
- Vendor Catalog
- Past Project Lessons Learned
- Failure Cases
- Commissioning Issues
- Maintenance Knowledge

## KnowledgeItem 필드

```text
code
version
knowledge_type
title
description
conditions_json
recommendations_json
constraints_json
references_json
valid_from
valid_to
review_status
reviewed_by
is_active
```

---

# 12. Rule Engine

Rule Engine은 JSON 기반 선언형 규칙을 지원한다.

## Rule 필드

```text
code
version
rule_type
priority
conditions_json
effects_json
explanation_template
severity
confidence
applicable_scope
is_active
```

예시:

```text
IF Tank Exists
AND Liquid Process
AND Continuous Level Measurement Required
AND Steam Present

THEN

Recommend Radar Level Measurement Principle
Require Analog Input
Require High Level Alarm
Require Low Level Alarm
Require Overflow Protection Review
Require HMI Trend
Generate FAT Sensor Simulation Test
Generate SAT Actual Level Verification Test
```

규칙은 Hard Rule과 Recommendation Rule로 구분한다.

Hard Rule은 자동으로 무시할 수 없다.

---

# 13. Design Engine

Design Engine은 다음 설계 결과를 생성한다.

```text
Process Design
Device Design
Sensor Design
I/O Design
Communication Design
PLC Sizing
PLC Architecture
HMI Information Architecture
Alarm Design
Interlock Design
Sequence Design
FAT Design
SAT Design
```

각 DesignDecision은 다음을 저장한다.

```text
project
decision_type
subject_type
subject_id
decision_value_json
reason
input_fact_ids
rule_ids
knowledge_item_ids
confidence
risk_level
approval_required
approval_status
version
created_at
```

---

# 14. Sensor Design 요구사항

센서 설계는 바로 특정 제조사 모델을 선택하지 않는다.

다음 순서로 설계한다.

```text
Measurement Requirement
→ Measurement Principle
→ Sensor Technology
→ Signal Type
→ Accuracy
→ Range
→ Response Time
→ Material Compatibility
→ Environmental Rating
→ Installation Constraints
→ Maintenance Requirements
→ Communication Requirements
→ Vendor Candidate
```

예:

```text
Level Measurement Required
→ Continuous
→ Non-contact
→ Steam Present
→ Radar Preferred
→ 4-20mA/HART Candidate
→ Required Range
→ Process Connection
→ IP Rating
→ Vendor Model Candidate
```

---

# 15. PLC Sizing 요구사항

PLC 선정은 단순 I/O 개수만 사용하지 않는다.

최소 다음 요소를 고려한다.

```text
DI Count
DO Count
AI Count
AO Count
High-Speed Counter
Pulse Output
Motion Axis
PID Loop Count
Safety I/O
Remote I/O
Communication Ports
Protocol Requirements
Scan Time Requirement
Memory Requirement
Data Logging
Redundancy
Future Expansion Margin
Existing Vendor Standard
Maintenance Capability
Spare Parts Policy
```

출력:

```text
Required PLC Class
Minimum Technical Specification
Candidate Vendors
Candidate Families
Selection Reason
Rejected Candidates and Reasons
```

---

# 16. Communication Design 요구사항

다음 구조를 생성한다.

```text
Device Communication Matrix
Protocol Compatibility Matrix
Network Segmentation
PLC-HMI Network
PLC-Remote I/O Network
PLC-Inverter/Servo Network
SCADA Network
MES/ERP Integration
OPC UA Requirement
MQTT Requirement
Gateway Requirement
Time Synchronization Requirement
Failure Behavior
Communication Alarm
```

---

# 17. HMI Design 요구사항

자동 생성 대상:

```text
Main Overview
Process Overview
Equipment Detail
Manual Operation
Auto Sequence
Alarm Summary
Alarm History
Trend
Recipe
I/O Monitor
Interlock Status
Maintenance
Communication Status
User Management
System Settings
Report
```

질문 답변과 설계 상태에 따라 필요한 화면만 생성한다.

각 화면은 다음을 가진다.

```text
Screen Name
Purpose
User Role
Required Tags
Commands
Status Objects
Alarm Objects
Trend Objects
Navigation
Security Level
```

---

# 18. Alarm / Interlock / Cause & Effect

## Alarm 필드

```text
code
source
condition
delay
priority
message
operator_action
reset_type
latching
related_interlock
fat_test_required
sat_test_required
```

## Interlock 필드

```text
code
protected_device
condition
effect
reset_condition
bypass_allowed
bypass_permission
safety_related
reason
fat_test_required
sat_test_required
```

Cause & Effect Matrix는 Alarm과 Interlock 데이터를 기반으로 생성한다.

---

# 19. Sequence Design

## Sequence Step 필드

```text
sequence
step_no
name
entry_condition
actions
completion_condition
timeout
timeout_alarm
abort_condition
hold_condition
resume_condition
next_step
fallback_step
```

Sequence는 Vendor Independent IR로 먼저 생성한다.

---

# 20. Vendor Independent IR

모든 제조사별 코드 생성기는 공통 IR을 입력으로 사용한다.

IR 최소 구성:

```text
ProjectMetadata
DeviceDefinitions
SignalDefinitions
DataTypes
FunctionBlockInstances
LogicExpressions
Timers
Counters
Comparisons
ArithmeticOperations
MoveOperations
ControlOperations
Sequences
Alarms
Interlocks
HMITags
CommunicationMappings
TestRequirements
```

기능장 및 PLC 실무에서 중요한 다음 연산을 명시적으로 표현할 수 있어야 한다.

```text
ADD
SUB
MUL
DIV
COMPARE
MOVE
WORD_OPERATION
BIT_OPERATION
TIMER
COUNTER
SET_RESET
CONTROL_FLOW
```

---

# 21. Vendor Adapter

초기 개발 순서:

1. LS ELECTRIC Adapter
2. Siemens Adapter
3. Mitsubishi Adapter

각 Adapter는 다음 인터페이스를 구현한다.

```text
validate_ir()
map_data_types()
map_addresses()
map_instructions()
generate_program_structure()
generate_tags()
generate_alarm_mapping()
generate_hmi_tags()
generate_test_artifacts()
package_output()
```

초기 MVP에서는 실제 제조사 프로젝트 바이너리 파일 생성보다 다음을 우선한다.

- Structured Text 출력
- Ladder Intermediate Representation
- Tag CSV
- I/O CSV
- Alarm CSV
- HMI Tag CSV
- Vendor Mapping Report

---

# 22. Validation Engine

검증기는 최소 다음 검사를 수행한다.

```text
Missing Requirement Check
Missing Sensor Check
I/O Consistency Check
Duplicate Tag Check
Address Collision Check
Signal Type Mismatch
Range Mismatch
Unit Mismatch
Protocol Compatibility Check
PLC Capacity Check
Communication Port Check
Alarm Coverage Check
Interlock Coverage Check
Sequence Dead-End Check
Sequence Timeout Check
Unreachable Step Check
Unsafe Bypass Check
FAT Coverage Check
SAT Coverage Check
Traceability Coverage Check
```

## ValidationFinding

```text
severity
code
title
description
related_objects
recommended_action
status
```

## Severity

```text
INFO
WARNING
ERROR
CRITICAL
```

CRITICAL이 존재하면 Vendor Code Generation을 금지한다.

---

# 23. Approval Workflow

Approval 대상:

```text
Requirement Baseline
Sensor Design
PLC Design
Communication Design
HMI Design
Alarm/Interlock Design
Sequence Design
FAT Plan
SAT Plan
Vendor Code Generation
As-Built Release
```

Approval 상태:

```text
DRAFT
IN_REVIEW
APPROVED
REJECTED
SUPERSEDED
```

---

# 24. FAT/SAT

FAT Test Case 자동 생성 입력:

```text
Requirement
Device
Sensor
I/O
Alarm
Interlock
Sequence
HMI
Communication
```

## FAT Test Case

```text
test_id
category
precondition
procedure
expected_result
actual_result
status
evidence
tester
reviewer
```

SAT는 실제 현장 조건과 Commissioning 결과를 추가한다.

---

# 25. 감사로그와 버전관리

다음 변경을 모두 기록한다.

```text
질문 변경
답변 변경
Fact 변경
Rule 적용
Knowledge 변경
Design Decision 생성/변경
승인/거절
Vendor Code 생성
FAT/SAT 결과
문서 생성
```

## AuditEvent

```text
actor
action
object_type
object_id
before_json
after_json
reason
timestamp
```

---

# 26. MVP 범위

MVP에서는 다음을 구현한다.

1. Company CRUD
2. Project CRUD
3. Question CRUD
4. AnswerOption CRUD
5. InterviewSession
6. InterviewAnswer
7. ProjectFact
8. ProjectState Projection
9. KnowledgeItem
10. Rule
11. Question Engine
12. Answer Processor
13. Rule Engine
14. DesignDecision
15. Sensor Recommendation
16. I/O Estimation
17. PLC Requirement/Sizing
18. Communication Recommendation
19. HMI Screen Recommendation
20. Alarm Recommendation
21. Interlock Recommendation
22. FAT/SAT Test Draft
23. ValidationFinding
24. Design Review UI
25. Human Approval
26. Excel Export

MVP에서 제외:

```text
실제 Siemens 프로젝트 파일 생성
실제 LS ELECTRIC 프로젝트 파일 생성
실제 Mitsubishi 프로젝트 파일 생성
Safety PLC 자동 코드 생성
완전자율 Vendor Code Deployment
P&ID CAD 자동 생성
Digital Twin
```

---

# 27. 초기 지식베이스 범위

## Industry

```text
식품
수처리
일반 제조
물류
스마트팜
```

## Process

```text
Tank Storage
Liquid Transfer
Mixing
Heating
Cooling
Conveyor Transfer
Packaging
Inspection
Batch Process
Continuous Process
```

## Device

```text
Motor
Pump
Valve
Tank
Cylinder
Conveyor
Heater
Fan
Inverter
Emergency Stop
```

## Sensor

```text
Level
Temperature
Pressure
Flow
Proximity
Photoelectric
Load Cell
Current
Vibration
Encoder
```

---

# 28. 초기 질문 데이터 목표

```text
Phase 1: 50개
Phase 2: 150개
Phase 3: 업종별 300개 이상
```

질문 수 자체를 KPI로 사용하지 않는다.

핵심 KPI:

```text
Critical Requirement Coverage
Average Questions to Design Readiness
Unnecessary Question Rate
Design Decision Confidence
Expert Override Rate
Validation Finding Rate
FAT Defect Escape Rate
SAT Defect Escape Rate
```

---

# 29. API 요구사항

```text
/api/companies/
/api/projects/
/api/questions/
/api/knowledge-items/
/api/rules/
/api/interview/sessions/
/api/interview/sessions/{id}/next-question/
/api/interview/sessions/{id}/answer/
/api/interview/sessions/{id}/facts/
/api/interview/sessions/{id}/state/
/api/interview/sessions/{id}/progress/
/api/projects/{id}/generate-design/
/api/projects/{id}/design-decisions/
/api/projects/{id}/validation-findings/
/api/projects/{id}/submit-review/
/api/projects/{id}/approvals/
/api/projects/{id}/fat-tests/
/api/projects/{id}/sat-tests/
/api/projects/{id}/export/
```

---

# 30. Frontend 주요 화면

```text
Login
Company List
Company Detail
Project List
Project Dashboard
Interview Start
Adaptive Interview
Interview Progress
Current Project State
Missing Information
Detected Risks
Design Preview
Sensor Design
I/O List
PLC Design
Communication Architecture
HMI Screen Definition
Alarm Matrix
Interlock Matrix
Sequence Table
Validation Findings
Design Approval
FAT Plan
SAT Plan
Document Export
Audit History
```

---

# 31. 테스트 요구사항

Backend:

```text
pytest
pytest-django
factory-boy
```

Frontend:

```text
Vitest
React Testing Library
```

E2E:

```text
Playwright
```

필수 테스트:

```text
Question Selection Test
Answer Normalization Test
Fact Generation Test
Rule Matching Test
Conflict Detection Test
Design Decision Traceability Test
Sensor Recommendation Test
PLC Sizing Test
Communication Compatibility Test
HMI Screen Generation Test
Alarm/Interlock Generation Test
FAT/SAT Coverage Test
Critical Validation Blocking Test
Approval Workflow Test
```

---

# 32. 개발 단계

## Phase 0 — Repository Bootstrap

Django/React/PostgreSQL/Docker 환경 구축  
Lint/Format/Test 설정  
환경변수 관리  
README 작성

## Phase 1 — Core Domain

Company  
Project  
Question  
InterviewSession  
InterviewAnswer  
ProjectFact  
KnowledgeItem  
Rule  
DesignDecision

## Phase 2 — Question Engine

질문 후보 필터링  
질문 점수 계산  
다음 질문 선택  
선택 이유 기록  
인터뷰 종료조건

## Phase 3 — Knowledge & Rule Engine

초기 지식 데이터  
Rule Matcher  
Effect Executor  
Conflict Detection

## Phase 4 — Design Engine

Sensor  
I/O  
PLC  
Communication  
HMI  
Alarm  
Interlock  
FAT/SAT

## Phase 5 — Validation & Approval

Validation Engine  
Finding UI  
Review Queue  
Approval Workflow

## Phase 6 — Frontend

Adaptive Interview  
Project State  
Design Preview  
Validation  
Approval  
Export

## Phase 7 — LS ELECTRIC Adapter PoC

Vendor Independent IR  
ST Generator  
Tag Export  
I/O Export  
Alarm Export  
Vendor Mapping Report

---

# 33. Claude Code 작업 원칙

1. PRD 전체를 읽고 구현 전 PLAN.md를 작성한다.
2. 한 번에 전체 프로젝트를 구현하지 않는다.
3. Phase 단위로 작업한다.
4. 각 Phase 시작 전 TASKS.md를 작성한다.
5. 각 Task 완료 후 테스트를 실행한다.
6. 실패한 테스트를 삭제하거나 우회하지 않는다.
7. 모델 변경 시 Migration을 생성한다.
8. Business Logic은 ViewSet과 Serializer에 직접 작성하지 않는다.
9. Django Signal을 핵심 비즈니스 워크플로에 사용하지 않는다.
10. Service Layer와 Selector Layer를 사용한다.
11. 모든 DesignDecision은 Traceability 정보를 가져야 한다.
12. LLM 호출은 Interface로 추상화한다.
13. LLM이 없어도 Rule-based MVP가 동작해야 한다.
14. CRITICAL ValidationFinding이 존재하면 Vendor Generation을 차단한다.
15. Safety 관련 Rule은 명시적 승인 없이 비활성화하지 않는다.
16. PostgreSQL JSONField를 사용하되 핵심 검색 필드는 정규화한다.
17. 질문, 규칙, 지식은 Version 관리가 가능해야 한다.
18. 모든 외부 입력을 검증한다.
19. API 오류 응답 형식을 통일한다.
20. UTF-8을 기본 인코딩으로 사용하고 한글 데이터 깨짐 테스트를 작성한다.
21. 작업 완료 후 코드 리뷰를 수행한다.
22. 구현과 검증을 가능하면 서로 다른 Agent Context에서 수행한다.
23. 각 Phase 종료 시 WORKLOG.md를 갱신한다.
24. 다음 Phase로 넘어가기 전 사용자 승인 포인트를 제공한다.

---

# 34. Claude Code 최초 실행 명령

먼저 이 PRD를 기준으로 Repository를 분석하고 개발 계획만 작성한다.

아직 전체 기능을 구현하지 마라.

다음을 수행하라.

1. 현재 Repository 구조를 확인한다.
2. PRD 요구사항과 현재 코드의 Gap Analysis를 수행한다.
3. 목표 아키텍처를 제안한다.
4. Django App Boundary를 확정한다.
5. 핵심 Domain Model과 관계를 Mermaid ERD로 작성한다.
6. Question Engine 실행 흐름을 Mermaid Sequence Diagram으로 작성한다.
7. Phase 0~7 개발 계획을 PLAN.md로 작성한다.
8. Phase 0의 세부 작업을 TASKS.md로 작성한다.
9. 주요 기술 리스크와 대응방안을 RISKS.md로 작성한다.
10. Acceptance Criteria를 ACCEPTANCE_CRITERIA.md로 작성한다.
11. 개발에 앞서 사용자 결정이 필요한 사항을 DECISIONS_REQUIRED.md로 작성한다.

중요:

- 아직 전체 프로젝트를 구현하지 마라.
- 기존 파일을 무분별하게 삭제하거나 덮어쓰지 마라.
- PRD와 충돌하는 기존 구현이 있다면 먼저 보고하라.
- 추정한 내용과 확정된 요구사항을 구분하라.
- 산업 안전 관련 기능은 자동 확정하지 마라.
- 모든 계획은 테스트 가능하고 작은 Task 단위로 작성하라.

작업 완료 후 다음 형식으로 보고하라.

```text
SUMMARY

CURRENT REPOSITORY STATUS

GAP ANALYSIS

PROPOSED ARCHITECTURE

FILES CREATED

KEY RISKS

DECISIONS REQUIRED

PHASE 0 READY CHECK

RECOMMENDED NEXT COMMAND
```

---

# 35. 다음 확장 문서

이 PRD 이후 다음 문서를 추가로 작성한다.

```text
CLAUDE.md
PLAN.md
TASKS.md
RISKS.md
ACCEPTANCE_CRITERIA.md
DECISIONS_REQUIRED.md
QUESTION_ENGINE_SPEC.md
KNOWLEDGE_BASE_SPEC.md
RULE_ENGINE_SPEC.md
VENDOR_IR_SPEC.md
```
