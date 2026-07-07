import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setBusy(true)
    try {
      await login(username, password)
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : '로그인 실패')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="container" style={{ maxWidth: 400 }}>
      <div className="panel">
        <h1>PLC-Forge 로그인</h1>
        <form onSubmit={onSubmit}>
          <label htmlFor="username">사용자명</label>
          <input
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
          />
          <label htmlFor="password">비밀번호</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
          />
          {error && (
            <p className="error-text" role="alert" style={{ marginTop: '0.75rem' }}>
              {error}
            </p>
          )}
          <button className="btn" type="submit" disabled={busy} style={{ marginTop: '1rem' }}>
            {busy ? '로그인 중…' : '로그인'}
          </button>
        </form>
      </div>
    </div>
  )
}
