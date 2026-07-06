# TASKS.md — Phase 1: Core Domain

**목표:** MVP 항목 1~10의 도메인 모델과 CRUD API를 Service Layer 구조로 구현한다.
비즈니스 로직은 services.py, 조회는 selectors.py에 둔다 (PRD §33-8,10).
(Phase 0 작업 내역은 WORKLOG.md 참조)

## T1.1 accounts — 커스텀 User + JWT 인증 (D1: JWT 확정)
- `apps.accounts.User(AbstractUser)` + UUID PK + role(PRD §4의 6개 역할 + ADMIN)
- djangorestframework-simplejwt: `/api/auth/token/`, `/api/auth/token/refresh/`
- 기본 권한 IsAuthenticated (health 등 공개 엔드포인트 제외)
- ✓ 토큰 발급/갱신 테스트, 미인증 401이 통일 오류 포맷으로 반환

## T1.2 companies — Company CRUD
- ✓ 목록/생성/조회/수정 테스트

## T1.3 projects — Project CRUD
- company FK, code unique, status 상태값, created_by
- ✓ CRUD 테스트

## T1.4 interview — Question / AnswerOption / InterviewSession / InterviewAnswer
- Question: PRD §8.2 전체 필드, §8.3 유형 12종, §8.4 카테고리, (code, version) unique
- answer_schema는 유효한 JSON Schema여야 함 (jsonschema로 검증)
- InterviewSession 생성/조회 + `POST /api/interview/sessions/{id}/answer/` (저장만, 엔진은 Phase 2)
- ✓ 질문 CRUD, 잘못된 answer_schema 거부, 답변 제출 테스트

## T1.5 requirements — ProjectFact + FactStatus 상태기계
- PRD §10 필드, (project, fact_key, version) unique
- 상태 전이 규칙: PROPOSED→{CONFIRMED,CONFLICTED,REJECTED}, CONFLICTED→{CONFIRMED,REJECTED},
  CONFIRMED→{SUPERSEDED,CONFLICTED}; SUPERSEDED/REJECTED는 종료 상태
- 동일 fact_key 재생성 시 version 자동 증가 + 이전 활성 Fact SUPERSEDED
- ✓ 허용/거부 전이 테스트, 버전 증가 테스트, API 전이 엔드포인트 테스트

## T1.6 knowledge — KnowledgeItem CRUD
- PRD §11 필드, 8계층 knowledge_type
- ✓ CRUD 테스트

## T1.7 design — Rule + DesignDecision (Traceability 강제)
- Rule: PRD §12 필드, HARD/RECOMMENDATION 구분
- DesignDecision: PRD §13 필드, input_facts/rules/knowledge_items M2M(정규화 조인 테이블)
- **Traceability 없는(연결 0개 또는 reason 없는) Decision은 서비스에서 생성 거부**
- ✓ 강제 규칙 테스트, CRUD 테스트

## T1.8 audit — AuditEvent
- PRD §25 필드, `record_event()` 서비스
- Fact 전이/답변 제출/Decision 생성 시 감사로그 기록
- ✓ 서비스 호출 → AuditEvent 생성 검증 테스트

## T1.9 API 배선 + 공통 규약
- DRF 라우터, 페이지네이션(PageNumber, 20), DomainError → 통일 오류 포맷 매핑
- ✓ 전체 pytest green, ruff clean, makemigrations --check clean

## Phase 1 Exit Checklist
- [ ] MVP 1~10 모델 CRUD + 테스트
- [ ] answer_schema JSON Schema 검증
- [ ] FactStatus 상태기계 강제
- [ ] DesignDecision Traceability 강제
- [ ] 빈 DB에서 마이그레이션 재적용 가능
- [ ] 쓰기 로직이 services.py에 위치
- [ ] WORKLOG.md 갱신 + 사용자 승인
