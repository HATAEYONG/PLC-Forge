import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import ApprovalTab from '../features/approval/ApprovalTab'
import DesignTab from '../features/design/DesignTab'
import InterviewTab from '../features/interview/InterviewTab'
import ValidationTab from '../features/validation/ValidationTab'

const TABS = [
  { key: 'interview', label: '인터뷰' },
  { key: 'design', label: '설계' },
  { key: 'validation', label: '검증' },
  { key: 'approval', label: '승인' },
] as const

type TabKey = (typeof TABS)[number]['key']

export default function ProjectWorkspace() {
  const { id } = useParams<{ id: string }>()
  const [tab, setTab] = useState<TabKey>('interview')
  if (!id) return null

  return (
    <div className="container">
      <p className="muted">
        <Link to="/">← 프로젝트 목록</Link>
      </p>
      <div className="row" style={{ gap: '0.4rem', marginBottom: '1rem' }}>
        {TABS.map((t) => (
          <button
            key={t.key}
            className={`btn ${tab === t.key ? '' : 'secondary'}`}
            onClick={() => setTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'interview' && <InterviewTab projectId={id} />}
      {tab === 'design' && <DesignTab projectId={id} />}
      {tab === 'validation' && <ValidationTab projectId={id} />}
      {tab === 'approval' && <ApprovalTab projectId={id} />}
    </div>
  )
}
