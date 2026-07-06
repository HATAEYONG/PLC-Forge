# PLC-Forge

![CI](https://github.com/HATAEYONG/PLC-Forge/actions/workflows/ci.yml/badge.svg)

AI 기반 산업 자동화 자율설계 플랫폼.

자동화 전문가가 고객과 현장 인터뷰를 수행하는 사고 과정을 소프트웨어로 구현하여,
적응형 질문(Question Engine) → 요구사항 구조화 → 자율설계 → 검증 → Human Approval →
PLC/HMI/통신 설계 생성 → FAT/SAT → 납품문서까지를 하나의 추적 가능한 흐름으로 만든다.

```text
현장 인터뷰 → 요구사항 구조화 → 자율설계 → 설계 검증 → Human Approval
→ PLC/HMI/통신 설계 생성 → FAT/SAT → 납품문서
```

## 기술 스택

- Backend: Django 5 + Django REST Framework + PostgreSQL 16
- Frontend: React 18 (Vite) + TypeScript
- Infra: Docker Compose
- Test: pytest / Vitest / Playwright(예정)

## 시작하기

### Docker Compose (권장)

```bash
cp .env.example .env
docker compose up --build
# backend:  http://localhost:8000/api/health/
# frontend: http://localhost:5173
```

### 수동 실행

```bash
# 1. PostgreSQL 16 준비 후 .env.example 참고해 환경변수 설정

# 2. Backend
cd backend
python3 -m venv ../.venv && source ../.venv/bin/activate
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py runserver          # http://127.0.0.1:8000

# 3. Frontend (새 터미널)
cd frontend
npm install
npm run dev                          # http://127.0.0.1:5173 (/api → backend 프록시)
```

### 테스트 / 린트

```bash
make test    # backend pytest + frontend vitest
make lint    # ruff + eslint + prettier + tsc
```

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

**Phase 0 (Repository Bootstrap) 완료 — Phase 1 (Core Domain) 착수 대기.**
진행 내역은 `WORKLOG.md`, 다음 단계 결정 사항은 `DECISIONS_REQUIRED.md` 참조.
