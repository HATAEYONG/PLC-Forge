import { useCallback, useEffect, useState } from 'react'
import { api } from '../../api/client'
import { downloadFile } from '../../api/download'
import type { Paginated } from '../../types/api'
import type {
  Alarm,
  CauseEffectMatrix,
  DesignDecision,
  IOPoint,
  Interlock,
  PLCSizing,
  SensorRequirement,
  Sequence,
} from '../../types/design'

interface Bundle {
  sensors: SensorRequirement[]
  io: IOPoint[]
  plc: PLCSizing[]
  alarms: Alarm[]
  interlocks: Interlock[]
  sequences: Sequence[]
  decisions: DesignDecision[]
  causeEffect: CauseEffectMatrix | null
}

export default function DesignTab({ projectId }: { projectId: string }) {
  const [data, setData] = useState<Bundle | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [msg, setMsg] = useState<string | null>(null)

  const load = useCallback(async () => {
    const q = `?project=${projectId}`
    const [sensors, io, plc, alarms, interlocks, sequences, decisions, causeEffect] =
      await Promise.all([
        api.get<Paginated<SensorRequirement>>(`/api/sensor-requirements/${q}`),
        api.get<Paginated<IOPoint>>(`/api/io-points/${q}`),
        api.get<Paginated<PLCSizing>>(`/api/plc-sizing/${q}`),
        api.get<Paginated<Alarm>>(`/api/alarms/${q}`),
        api.get<Paginated<Interlock>>(`/api/interlocks/${q}`),
        api.get<Paginated<Sequence>>(`/api/sequences/${q}`),
        api.get<Paginated<DesignDecision>>(`/api/design-decisions/${q}`),
        api
          .get<CauseEffectMatrix>(`/api/projects/${projectId}/cause-effect-matrix/`)
          .catch(() => null),
      ])
    setData({
      sensors: sensors.results,
      io: io.results,
      plc: plc.results,
      alarms: alarms.results,
      interlocks: interlocks.results,
      sequences: sequences.results,
      decisions: decisions.results,
      causeEffect,
    })
  }, [projectId])

  useEffect(() => {
    void load()
  }, [load])

  async function run() {
    setBusy(true)
    setError(null)
    setMsg(null)
    try {
      await api.post(`/api/projects/${projectId}/apply-rules/`)
      const res = await api.post<{ summary: Record<string, unknown> }>(
        `/api/projects/${projectId}/generate-design/?stage=all`,
      )
      setMsg('설계 생성 완료: ' + JSON.stringify(res.summary))
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : '설계 생성 실패')
    } finally {
      setBusy(false)
    }
  }

  async function generateVendor() {
    setBusy(true)
    setError(null)
    setMsg(null)
    try {
      const res = await api.post<{ vendor: string; mapping_report: { signal_count: number } }>(
        `/api/projects/${projectId}/vendor-generate/?vendor=ls`,
      )
      setMsg(`${res.vendor} 코드 생성 완료 (신호 ${res.mapping_report.signal_count}개, ST+CSV 6종)`)
    } catch (err) {
      // CRITICAL 차단 시 여기서 오류 메시지 노출
      setError(err instanceof Error ? err.message : '벤더 코드 생성 실패')
    } finally {
      setBusy(false)
    }
  }

  if (!data) return <p className="muted">불러오는 중…</p>

  const io = data.io
  const counts = ['DI', 'DO', 'AI', 'AO'].map(
    (s) => `${s} ${io.filter((p) => p.signal_type === s).length}`,
  )

  return (
    <div>
      <div className="panel">
        <div className="row" style={{ justifyContent: 'space-between' }}>
          <h2 style={{ margin: 0 }}>설계 생성</h2>
          <div className="row">
            <button
              className="btn secondary"
              onClick={() =>
                downloadFile(`/api/projects/${projectId}/export/`, 'PLC-Forge.xlsx').catch((e) =>
                  setError(e instanceof Error ? e.message : 'Export 실패'),
                )
              }
            >
              ⬇ Excel Export
            </button>
            <button className="btn secondary" onClick={generateVendor} disabled={busy}>
              LS 코드 생성
            </button>
            <button className="btn" onClick={run} disabled={busy}>
              {busy ? '생성 중…' : '규칙 적용 + 설계 생성'}
            </button>
          </div>
        </div>
        {msg && <p className="muted">{msg}</p>}
        {error && <p className="error-text">{error}</p>}
      </div>

      <Section title={`센서 요구사항 (${data.sensors.length})`}>
        <table>
          <thead>
            <tr>
              <th>측정</th>
              <th>원리</th>
              <th>신호</th>
              <th>환경/재질</th>
            </tr>
          </thead>
          <tbody>
            {data.sensors.map((s) => (
              <tr key={s.id}>
                <td>{s.measurement_type}</td>
                <td>{s.measurement_principle}</td>
                <td>{s.signal_type}</td>
                <td className="muted">
                  {[s.environmental_rating, s.material_compatibility].filter(Boolean).join(' · ')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Section>

      <Section title={`I/O List (${io.length}) — ${counts.join(' / ')}`}>
        <table>
          <thead>
            <tr>
              <th>태그</th>
              <th>신호</th>
              <th>설명</th>
            </tr>
          </thead>
          <tbody>
            {io.map((p) => (
              <tr key={p.id}>
                <td>{p.tag}</td>
                <td>
                  <span className="badge">{p.signal_type}</span>
                </td>
                <td className="muted">{p.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Section>

      {data.plc.map((sizing) => (
        <Section key={sizing.id} title={`PLC Sizing — ${sizing.required_class}`}>
          <p className="muted">{sizing.selection_reason}</p>
          <table>
            <thead>
              <tr>
                <th>벤더</th>
                <th>제품군</th>
                <th>채택</th>
                <th>사유</th>
              </tr>
            </thead>
            <tbody>
              {sizing.candidates.map((c) => (
                <tr key={c.id}>
                  <td>{c.vendor}</td>
                  <td>{c.family}</td>
                  <td>{c.accepted ? '✅' : '❌'}</td>
                  <td className="muted">{c.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Section>
      ))}

      <Section title={`알람 (${data.alarms.length})`}>
        {data.alarms.map((a) => (
          <div key={a.id} className="row" style={{ marginBottom: '0.3rem' }}>
            <span className={`badge ${a.priority}`}>{a.priority}</span>
            <strong>{a.code}</strong>
            <span className="muted">{a.condition}</span>
          </div>
        ))}
      </Section>

      <Section title={`인터록 (${data.interlocks.length})`}>
        {data.interlocks.map((i) => (
          <div key={i.id} className="row" style={{ marginBottom: '0.3rem' }}>
            {i.safety_related && <span className="badge CRITICAL">SAFETY</span>}
            <strong>{i.code}</strong>
            <span className="muted">
              {i.effect} · 바이패스 {i.bypass_allowed ? i.bypass_permission || '허용' : '금지'}
            </span>
          </div>
        ))}
      </Section>

      {data.sequences.map((seq) => (
        <Section key={seq.id} title={`시퀀스 — ${seq.name}`}>
          <ol>
            {seq.steps.map((st) => (
              <li key={st.id}>
                {st.name} <span className="muted">→ {st.completion_condition}</span>
              </li>
            ))}
          </ol>
        </Section>
      ))}

      {data.causeEffect && data.causeEffect.causes.length > 0 && (
        <Section title="Cause & Effect Matrix">
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>원인 \ 결과</th>
                  {data.causeEffect.effects.map((e) => (
                    <th key={e}>{e}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.causeEffect.matrix.map((row) => (
                  <tr key={row.cause}>
                    <td>{row.cause}</td>
                    {data.causeEffect!.effects.map((e) => (
                      <td key={e}>{row.effects[e] ? '✕' : ''}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>
      )}

      <Section title={`설계 결정 근거 (${data.decisions.length})`}>
        <table>
          <thead>
            <tr>
              <th>결정</th>
              <th>대상</th>
              <th>근거</th>
              <th>신뢰도/위험</th>
            </tr>
          </thead>
          <tbody>
            {data.decisions.slice(0, 30).map((d) => (
              <tr key={d.id}>
                <td>{d.decision_type}</td>
                <td className="muted">
                  {d.subject_type}
                  {d.subject_id ? `/${d.subject_id}` : ''}
                </td>
                <td className="muted">
                  Fact {d.input_facts.length} · 규칙 {d.rules.length} · 지식{' '}
                  {d.knowledge_items.length}
                </td>
                <td>
                  {d.confidence.toFixed(2)}{' '}
                  <span className={`badge ${d.risk_level}`}>{d.risk_level}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Section>
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="panel">
      <h3>{title}</h3>
      {children}
    </div>
  )
}
