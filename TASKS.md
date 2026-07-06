# TASKS.md — Phase 0: Repository Bootstrap

**목표:** `docker compose up` 한 번으로 개발환경이 뜨고, 양쪽 테스트/린트가 통과하는
빈 골격을 만든다. 비즈니스 로직은 포함하지 않는다.

각 Task는 독립적으로 검증 가능해야 하며, 완료 조건(✓)을 만족한 뒤 커밋한다.

---

## T0.1 저장소 기본 파일
- `.gitignore`(Python/Node/IDE/env), `.editorconfig`, `README.md`(설치/실행 방법)
- ✓ 신규 클론에서 README만 보고 개발환경 기동 가능

## T0.2 Backend 스캐폴드
- `backend/` Django 5.x 프로젝트 생성, `config/settings/{base,dev,prod}.py` 분리
- `django-environ`(또는 os.environ) 기반 환경변수 로딩, `.env.example` 작성
- DRF 설치, `core/` 앱: BaseModel(UUID PK, created_at/updated_at), 공통 예외 핸들러
- ✓ `python manage.py check` 통과, `runserver` 기동

## T0.3 통일 API 오류 응답 포맷 (PRD §33-19)
- 형식: `{"error": {"code": str, "message": str, "details": object|null}}`
- DRF `EXCEPTION_HANDLER` 등록, ValidationError/404/500 케이스 테스트
- ✓ 오류 포맷 단위 테스트 3건 통과

## T0.4 PostgreSQL + Docker Compose
- `docker-compose.yml`: postgres:16(+healthcheck, 볼륨), backend, frontend
- DB 접속 정보는 환경변수로만 주입, 클라이언트 인코딩 UTF-8 명시
- ✓ `docker compose up` 후 backend가 DB 마이그레이션 실행 성공

## T0.5 Health Endpoint
- `GET /api/health/` → `{status, db, version}` (DB 연결 확인 포함)
- ✓ 통합 테스트 1건 통과

## T0.6 Backend 테스트/린트 체인
- pytest + pytest-django + factory-boy 설정 (`pyproject.toml`)
- ruff(lint+format) 설정, `make test` / `make lint` (또는 스크립트)
- ✓ 빈 테스트 스위트 green, ruff clean

## T0.7 한글 UTF-8 왕복 테스트 (PRD §33-20)
- 임시 모델 없이 health/echo 수준에서: 한글 문자열 JSON 요청→DB 저장→조회 왕복 테스트
  (core에 최소 KeyValue 테스트 모델 사용, 마이그레이션 포함)
- ✓ "탱크가 3개 있고 온도는 80℃" 왕복 후 바이트 동일성 검증 통과

## T0.8 Frontend 스캐폴드
- `frontend/` Vite + React 18 + TypeScript, 라우터, `src/` 디렉터리 구조(PRD §7)
- axios(또는 fetch wrapper) `api/client.ts`, health 호출하는 플레이스홀더 페이지
- ✓ `npm run dev` 기동, health 상태가 화면에 표시

## T0.9 Frontend 테스트/린트 체인
- Vitest + React Testing Library, ESLint + Prettier
- ✓ 샘플 컴포넌트 테스트 1건 통과, lint clean

## T0.10 CI 워크플로 (GitHub Actions)
- backend: ruff + pytest / frontend: eslint + vitest / PR마다 실행
- ✓ CI green 뱃지 README에 추가

## T0.11 WORKLOG.md 초기화
- Phase 0 수행 내역 기록 양식 작성
- ✓ Phase 0 종료 시점에 갱신됨

---

## Phase 0 Exit Checklist
- [ ] `docker compose up` → backend health 200 + frontend 렌더
- [ ] backend: pytest / ruff 통과
- [ ] frontend: vitest / eslint 통과
- [ ] 한글 UTF-8 왕복 테스트 통과
- [ ] CI green
- [ ] WORKLOG.md 갱신
- [ ] 사용자 승인 후 Phase 1 진행 (PRD §33-24)
