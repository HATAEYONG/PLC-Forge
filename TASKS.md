# TASKS.md — Phase 6-B: Frontend (설계 미리보기 · Validation · 승인)

**목표:** 프로젝트 워크스페이스를 탭 구조로 만들고, 설계 생성·미리보기, 검증 결과,
승인 워크플로 UI를 구현한다. (이전 내역은 WORKLOG.md 참조)

## T6B.1 프로젝트 워크스페이스 탭
- /projects/:id 를 탭(인터뷰 / 설계 / 검증 / 승인)으로 재구성
- InterviewPage → InterviewTab 컴포넌트로 이동
- ✓ 탭 전환 렌더

## T6B.2 설계 생성·미리보기 탭
- apply-rules / generate-design 실행 버튼
- 산출물 미리보기: 센서·I/O·PLC(후보/탈락사유)·통신·HMI·알람·인터록·시퀀스·Cause&Effect
- DesignDecision 근거(입력 Fact/규칙/지식/신뢰도) 열람
- ✓ 산출물 렌더 테스트

## T6B.3 Validation 탭
- validate 실행, Finding 심각도별 목록(CRITICAL 강조), 요약 카운트
- ✓ Finding 렌더 테스트

## T6B.4 승인 탭
- 승인 대상 제출(submit-review) + approve/reject, 상태·이력 표시
- CRITICAL 차단 시 오류 메시지 표시
- ✓ 승인 액션 렌더 테스트

## Phase 6-B Exit Checklist
- [ ] vitest green, eslint/prettier/tsc clean, 빌드 성공
- [ ] 설계 생성→미리보기→검증→승인 흐름 동작(백엔드 연동)
- [ ] CRITICAL 차단이 UI에 반영됨
- [ ] WORKLOG.md 갱신 + 사용자 승인 → Phase 6-C
