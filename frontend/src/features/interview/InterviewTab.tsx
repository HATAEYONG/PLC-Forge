import { useCallback, useEffect, useState } from 'react'
import { api } from '../../api/client'
import { QuestionWidget } from '../../components/QuestionWidget'
import type { Paginated } from '../../types/api'
import type {
  AnswerResponse,
  InterviewSession,
  NextQuestionResponse,
  ProgressResponse,
  ProjectFact,
} from '../../types/domain'

export default function InterviewTab({ projectId }: { projectId: string }) {
  const [session, setSession] = useState<InterviewSession | null>(null)
  const [next, setNext] = useState<NextQuestionResponse | null>(null)
  const [progress, setProgress] = useState<ProgressResponse | null>(null)
  const [lastFacts, setLastFacts] = useState<ProjectFact[]>([])
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const refresh = useCallback(async (sessionId: string) => {
    const [nq, pr] = await Promise.all([
      api.get<NextQuestionResponse>(`/api/interview/sessions/${sessionId}/next-question/`),
      api.get<ProgressResponse>(`/api/interview/sessions/${sessionId}/progress/`),
    ])
    setNext(nq)
    setProgress(pr)
  }, [])

  const startOrResume = useCallback(async () => {
    try {
      const existing = await api.get<Paginated<InterviewSession>>(
        `/api/interview/sessions/?project=${projectId}`,
      )
      const active = existing.results.find((s) => s.status === 'IN_PROGRESS')
      const s =
        active ??
        (await api.post<InterviewSession>('/api/interview/sessions/', {
          project: projectId,
        }))
      setSession(s)
      await refresh(s.id)
    } catch (err) {
      setError(err instanceof Error ? err.message : '세션 시작 실패')
    }
  }, [projectId, refresh])

  useEffect(() => {
    void startOrResume()
  }, [startOrResume])

  async function submitAnswer(rawAnswer: unknown) {
    if (!session || !next?.question) return
    setBusy(true)
    setError(null)
    try {
      const res = await api.post<AnswerResponse>(`/api/interview/sessions/${session.id}/answer/`, {
        question: next.question.id,
        raw_answer: rawAnswer,
      })
      setLastFacts(res.generated_facts)
      await refresh(session.id)
    } catch (err) {
      setError(err instanceof Error ? err.message : '답변 제출 실패')
    } finally {
      setBusy(false)
    }
  }

  if (error) return <p className="error-text">{error}</p>
  if (!next || !progress) return <p className="muted">불러오는 중…</p>

  return (
    <>
      <div className="panel">
        <div className="row" style={{ justifyContent: 'space-between' }}>
          <h2 style={{ margin: 0 }}>적응형 인터뷰</h2>
          <span className="muted">
            답변 {progress.answered_count} · 확보 Fact {progress.known_fact_count}
          </span>
        </div>
      </div>

      {next.complete ? (
        <div className="panel">
          <h3>✅ 인터뷰 종료조건 충족</h3>
          <p className="muted">설계를 생성할 수 있습니다.</p>
        </div>
      ) : next.question ? (
        <div className="panel">
          <div className="row">
            <span className={`badge ${next.question.criticality}`}>{next.question.category}</span>
            <span className="muted">{next.question.code}</span>
          </div>
          <h3>{next.question.text}</h3>
          {next.question.help_text && <p className="muted">{next.question.help_text}</p>}
          <QuestionWidget question={next.question} onSubmit={submitAnswer} busy={busy} />
          {next.selection && (
            <p className="muted" style={{ marginTop: '0.8rem' }}>
              🎯 {next.selection.reason}
            </p>
          )}
        </div>
      ) : (
        <div className="panel">
          <p className="muted">{next.message ?? '적용 가능한 질문이 없습니다.'}</p>
        </div>
      )}

      {lastFacts.length > 0 && (
        <div className="panel">
          <h3>방금 추출된 정보</h3>
          {lastFacts.map((f) => (
            <span key={f.id} className="fact-chip">
              {f.fact_key} = {JSON.stringify(f.value_json)}
              {f.unit ? ` ${f.unit}` : ''}
            </span>
          ))}
        </div>
      )}

      <div className="panel">
        <h3>설계 착수 준비 상태</h3>
        <table>
          <tbody>
            {Object.entries(progress.completion.criteria).map(([key, c]) => (
              <tr key={key}>
                <td>{c.satisfied ? '✅' : '⬜'}</td>
                <td>{key}</td>
                <td className="muted">{c.detail}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
