import { useCallback, useEffect, useState } from 'react'
import { api } from '../../api/client'
import type { Paginated } from '../../types/api'
import type { ValidationFinding } from '../../types/design'

const SEVERITY_ORDER = ['CRITICAL', 'ERROR', 'WARNING', 'INFO'] as const

export default function ValidationTab({ projectId }: { projectId: string }) {
  const [findings, setFindings] = useState<ValidationFinding[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    const res = await api.get<Paginated<ValidationFinding>>(
      `/api/validation-findings/?project=${projectId}`,
    )
    setFindings(res.results)
  }, [projectId])

  useEffect(() => {
    void load()
  }, [load])

  async function runValidation() {
    setBusy(true)
    setError(null)
    try {
      await api.post(`/api/projects/${projectId}/validate/`)
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : '검증 실패')
    } finally {
      setBusy(false)
    }
  }

  const counts = SEVERITY_ORDER.map((s) => ({
    severity: s,
    n: findings.filter((f) => f.severity === s).length,
  }))
  const hasCritical = counts.find((c) => c.severity === 'CRITICAL')!.n > 0

  return (
    <div>
      <div className="panel">
        <div className="row" style={{ justifyContent: 'space-between' }}>
          <h2 style={{ margin: 0 }}>검증</h2>
          <button className="btn" onClick={runValidation} disabled={busy}>
            {busy ? '검증 중…' : '검증 실행'}
          </button>
        </div>
        <div className="row" style={{ marginTop: '0.6rem' }}>
          {counts.map((c) => (
            <span key={c.severity} className={`badge ${c.severity}`}>
              {c.severity} {c.n}
            </span>
          ))}
        </div>
        {hasCritical && (
          <p className="error-text" role="alert" style={{ marginTop: '0.6rem' }}>
            ⛔ CRITICAL 항목이 있어 벤더 코드 생성/릴리스 승인이 차단됩니다.
          </p>
        )}
        {error && <p className="error-text">{error}</p>}
      </div>

      <div className="panel">
        <h3>검증 항목 ({findings.length})</h3>
        {findings.length === 0 && <p className="muted">검증을 실행하세요.</p>}
        <table>
          <tbody>
            {findings.map((f) => (
              <tr key={f.id}>
                <td>
                  <span className={`badge ${f.severity}`}>{f.severity}</span>
                </td>
                <td>
                  <strong>{f.title}</strong>
                  <div className="muted">{f.description}</div>
                  {f.recommended_action && <div className="muted">→ {f.recommended_action}</div>}
                </td>
                <td className="muted">{f.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
