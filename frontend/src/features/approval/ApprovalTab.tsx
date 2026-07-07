import { useCallback, useEffect, useState } from 'react'
import { api } from '../../api/client'
import type { Paginated } from '../../types/api'
import type { Approval } from '../../types/design'

const TARGETS: { value: string; label: string }[] = [
  { value: 'REQUIREMENT_BASELINE', label: '요구사항 Baseline' },
  { value: 'SENSOR_DESIGN', label: '센서 설계' },
  { value: 'PLC_DESIGN', label: 'PLC 설계' },
  { value: 'COMMUNICATION_DESIGN', label: '통신 설계' },
  { value: 'HMI_DESIGN', label: 'HMI 설계' },
  { value: 'ALARM_INTERLOCK_DESIGN', label: '알람/인터록 설계' },
  { value: 'SEQUENCE_DESIGN', label: '시퀀스 설계' },
  { value: 'FAT_PLAN', label: 'FAT 계획' },
  { value: 'SAT_PLAN', label: 'SAT 계획' },
  { value: 'VENDOR_CODE_GENERATION', label: '벤더 코드 생성' },
  { value: 'AS_BUILT_RELEASE', label: 'As-Built 릴리스' },
]

export default function ApprovalTab({ projectId }: { projectId: string }) {
  const [approvals, setApprovals] = useState<Approval[]>([])
  const [target, setTarget] = useState(TARGETS[0].value)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    const res = await api.get<Paginated<Approval>>(`/api/approvals/?project=${projectId}`)
    setApprovals(res.results)
  }, [projectId])

  useEffect(() => {
    void load()
  }, [load])

  async function act(fn: () => Promise<unknown>) {
    setError(null)
    try {
      await fn()
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : '요청 실패')
    }
  }

  const submit = () => act(() => api.post(`/api/projects/${projectId}/submit-review/`, { target }))
  const approve = (id: string) =>
    act(() => api.post(`/api/approvals/${id}/approve/`, { reason: '승인' }))
  const reject = (id: string) =>
    act(() => api.post(`/api/approvals/${id}/reject/`, { reason: '반려' }))

  return (
    <div>
      <div className="panel">
        <h2 style={{ marginTop: 0 }}>승인 요청</h2>
        <div className="row">
          <select value={target} onChange={(e) => setTarget(e.target.value)} style={{ flex: 1 }}>
            {TARGETS.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
          <button className="btn" onClick={submit}>
            검토 제출
          </button>
        </div>
        {error && (
          <p className="error-text" role="alert">
            {error}
          </p>
        )}
      </div>

      <div className="panel">
        <h3>승인 현황 ({approvals.length})</h3>
        <table>
          <thead>
            <tr>
              <th>대상</th>
              <th>상태</th>
              <th>액션</th>
            </tr>
          </thead>
          <tbody>
            {approvals.map((a) => (
              <tr key={a.id}>
                <td>{TARGETS.find((t) => t.value === a.target)?.label ?? a.target}</td>
                <td>
                  <span className="badge">{a.status}</span>
                </td>
                <td>
                  {a.status === 'IN_REVIEW' && (
                    <div className="row">
                      <button className="btn" onClick={() => approve(a.id)}>
                        승인
                      </button>
                      <button className="btn secondary" onClick={() => reject(a.id)}>
                        반려
                      </button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
