import { Link, Outlet } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Layout() {
  const { user, logout } = useAuth()
  return (
    <>
      <header className="app-header">
        <h1>
          <Link to="/">⚙️ PLC-Forge</Link>
        </h1>
        <div className="row">
          {user && <span className="muted">{user.username}</span>}
          <button className="btn secondary" onClick={logout}>
            로그아웃
          </button>
        </div>
      </header>
      <Outlet />
    </>
  )
}
