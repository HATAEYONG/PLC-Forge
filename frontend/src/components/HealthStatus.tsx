import { useEffect, useState } from 'react'
import { apiGet } from '../api/client'
import type { HealthResponse } from '../types/api'

export function HealthStatus() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    apiGet<HealthResponse>('/api/health/')
      .then(setHealth)
      .catch((e: Error) => setError(e.message))
  }, [])

  if (error) {
    return <p role="alert">백엔드 연결 실패: {error}</p>
  }
  if (!health) {
    return <p>백엔드 상태 확인 중…</p>
  }
  return (
    <p>
      백엔드 상태: <strong>{health.status}</strong> · DB {health.db ? '연결됨' : '오류'} · v
      {health.version}
    </p>
  )
}
