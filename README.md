# PLC-Forge

AI 기반 산업 자동화 자율설계 플랫폼.

자동화 전문가가 고객과 현장 인터뷰를 수행하는 사고 과정을 소프트웨어로 구현하여,
적응형 질문(Question Engine) → 요구사항 구조화 → 자율설계 → 검증 → Human Approval →
PLC/HMI/통신 설계 생성 → FAT/SAT → 납품문서까지를 하나의 추적 가능한 흐름으로 만든다.

```text
현장 인터뷰 → 요구사항 구조화 → 자율설계 → 설계 검증 → Human Approval
→ PLC/HMI/통신 설계 생성 → FAT/SAT → 납품문서
```

## 기술 스택 (예정)

- Backend: Django + Django REST Framework + PostgreSQL
- Frontend: React (Vite) + TypeScript
- Infra: Docker Compose
- Test: pytest / Vitest / Playwright

## 개발 원칙

1. **Question Engine First** — 코드 생성기보다 질문 엔진이 먼저다
2. **Vendor Independent First** — 모든 설계는 공통 IR을 거친다
3. **Deterministic Core, AI Assisted** — Safety 로직은 명시적 규칙으로, LLM은 보조로
4. **Evidence-Based Design** — 모든 설계 결정에 근거를 남긴다
5. **Human-in-the-Loop** — Safety/최종 선정/코드 생성은 승인 없이 확정하지 않는다
6. **Traceability First** — Requirement부터 Delivery Document까지 추적 가능해야 한다

## 문서

| 문서 | 내용 |
|---|---|
| [docs/PRD.md](docs/PRD.md) | 제품 요구사항 정의 (v1.0) |
| [PLAN.md](PLAN.md) | 목표 아키텍처, ERD, Question Engine 흐름, Phase 0~7 계획 |
| [TASKS.md](TASKS.md) | 현재 Phase(Phase 0) 세부 작업 |
| [RISKS.md](RISKS.md) | 기술 리스크와 대응방안 |
| [ACCEPTANCE_CRITERIA.md](ACCEPTANCE_CRITERIA.md) | Phase별 완료 판정 기준 |
| [DECISIONS_REQUIRED.md](DECISIONS_REQUIRED.md) | 착수 전 사용자 결정 필요 사항 |

## 현재 상태

**계획 수립 완료, Phase 0(Repository Bootstrap) 착수 대기.**
구현은 `DECISIONS_REQUIRED.md`의 결정 확인 후 Phase 단위로 진행한다.
