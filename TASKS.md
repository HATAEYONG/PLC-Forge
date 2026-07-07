# TASKS.md — Phase 6-A: Frontend (인증 · 프로젝트 · 적응형 인터뷰)

**목표:** React(Vite) SPA로 로그인(JWT) → 프로젝트 목록/생성 → 적응형 인터뷰
(다음질문·답변·생성 Fact·진행률)를 구현한다. (이전 내역은 WORKLOG.md 참조)

## T6A.1 API 클라이언트 + 인증
- `api/client.ts` — JWT 토큰 주입, get/post/patch, 통일 오류 포맷 파싱
- `auth/AuthContext.tsx` — 로그인/로그아웃, localStorage 토큰, 사용자 정보
- ✓ 클라이언트 오류 파싱 테스트

## T6A.2 라우팅 + 보호 라우트
- react-router: /login, / (프로젝트), /projects/:id (인터뷰)
- 미인증 시 /login 리다이렉트, 레이아웃(헤더/네비)
- ✓ 렌더 테스트

## T6A.3 로그인 화면
- 사용자명/비밀번호 → 토큰 발급 → 저장 → 리다이렉트, 오류 표시
- ✓ 로그인 폼 테스트

## T6A.4 프로젝트 목록/생성
- 회사 선택 + 프로젝트 CRUD(목록/생성), 상태 표시
- ✓ 목록 렌더 테스트

## T6A.5 적응형 인터뷰
- 세션 시작/조회, next-question(선택 이유 표시), 질문 유형별 위젯,
  답변 제출 → 생성 Fact 표시, 진행률/종료조건 표시
- 질문 유형 위젯: TEXT/YES_NO/SINGLE_CHOICE/MULTI_CHOICE/INTEGER/DECIMAL/UNIT_VALUE/
  DEVICE_LIST 등
- ✓ 질문 위젯 렌더/입력 테스트

## Phase 6-A Exit Checklist
- [ ] vitest green, eslint/prettier/tsc clean, 빌드 성공
- [ ] 로그인 → 프로젝트 → 인터뷰 흐름 동작 (백엔드 연동)
- [ ] 질문 유형별 입력 위젯 제공
- [ ] WORKLOG.md 갱신 + 사용자 승인 → Phase 6-B
