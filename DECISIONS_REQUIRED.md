# DECISIONS_REQUIRED.md — 개발 착수 전 사용자 결정 필요 사항

각 항목에 제안(기본값)을 표시했다. 별도 지시가 없으면 제안대로 진행한다.

## D1. 인증 방식
- 선택지: (a) Django 세션 + CSRF, (b) JWT(SimpleJWT), (c) 외부 IdP(OAuth)
- **제안: (b) JWT** — React SPA 분리 구조와 궁합, 추후 모바일/외부 연동 용이
- 영향: Phase 0~1의 accounts 설계

## D2. 배포 대상 환경
- 선택지: (a) 사내 서버(Docker Compose), (b) 클라우드 VM, (c) 컨테이너 플랫폼(K8s 등)
- **제안: (a)로 시작** — MVP 단계 단순성 우선. 컨테이너 이미지는 어디서든 재사용 가능
- 영향: prod settings, CI/CD 범위

## D3. LLM 제공자 및 사용 시점
- PRD상 LLM 없이 동작하는 Rule-based MVP가 우선(§33-13)
- 선택지: (a) MVP 전체를 LLM 없이 완성 후 도입, (b) Phase 2부터 Answer 구조화에 병행 도입
- **제안: (a)** — Interface만 Phase 2에 정의하고 실제 연동은 MVP 검증 후
- 결정 필요: 도입 시 제공자(Anthropic Claude 제안), API Key 관리 주체

## D4. conditions_json 규칙 문법
- 선택지: (a) JSONLogic 표준 채택, (b) 자체 DSL 정의
- **제안: (a) JSONLogic** — 검증된 문법, 파서 재작성 불필요. 표현 불가 규칙은
  등록제 Python Rule 클래스로 보완
- 영향: Rule Engine(Phase 3), Question required_conditions(Phase 2) — 동일 문법 공유

## D5. 초기 집중 업종
- §27은 5개 업종(식품/수처리/일반제조/물류/스마트팜)을 나열
- **제안: 식품 + 수처리 2개 업종 우선** — 질문/지식/규칙 저작을 깊이 있게, 나머지는 골격만
- 결정 필요: 실제 첫 고객/시연 대상 업종이 무엇인지

## D6. 도메인 데이터 저작 책임
- 질문 50개, 지식항목, 규칙의 내용은 자동화 전문가 지식이 필요
- 선택지: (a) 사용자가 검토/보완할 초안을 Claude가 작성, (b) 사용자가 원본 저작
- **제안: (a)** — 단, 모든 Safety 관련 질문/규칙은 사용자 검토 승인 후 fixture 반영
- 영향: Phase 2~3 일정

## D7. 다국어(i18n) 범위
- 선택지: (a) 한국어 단일, (b) 질문/지식 데이터 모델에 다국어 필드 예비
- **제안: (a) 한국어 단일** — UTF-8 처리만 보장. 다국어는 데이터 모델 변경 없이
  추후 번역 테이블 추가 가능하도록 문자열을 코드와 분리
- 영향: Question/KnowledgeItem 스키마

## D8. 단위계 기준
- **제안: SI 기준 저장 + 입력 단위 보존**(원본 단위와 변환값 동시 저장, pint 사용)
- 결정 필요: 현장 관행 단위(kgf/cm², ℃ 등) 표시 우선순위

## D9. Excel Export 범위 (MVP 26번)
- 선택지: (a) I/O List + Alarm/Interlock Matrix + FAT/SAT 시트, (b) 전 산출물
- **제안: (a)** — 실무에서 즉시 쓰이는 4종 우선
- 결정 필요: 사내 표준 양식(템플릿) 존재 여부 — 있으면 제공 요청

## D10. 저장소/브랜치 운영 (확정됨)
- ~~church-ai 저장소와의 충돌~~ → **`hataeyong/plc-forge` 신규 저장소로 확정** (2026-07-06)
- 결정 필요: 기본 브랜치 보호 정책, PR 필수 여부 (제안: main 직접 push는 Phase 0까지만,
  이후 PR + CI green 필수)
