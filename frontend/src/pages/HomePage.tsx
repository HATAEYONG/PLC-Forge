import { HealthStatus } from '../components/HealthStatus'

export default function HomePage() {
  return (
    <main style={{ fontFamily: 'sans-serif', padding: '2rem' }}>
      <h1>PLC-Forge</h1>
      <p>AI 기반 산업 자동화 자율설계 플랫폼 — Phase 0 부트스트랩</p>
      <HealthStatus />
    </main>
  )
}
