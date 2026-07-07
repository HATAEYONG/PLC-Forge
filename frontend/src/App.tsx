import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import { AuthProvider, useAuth } from './auth/AuthContext'
import LoginPage from './pages/LoginPage'
import ProjectWorkspace from './pages/ProjectWorkspace'
import ProjectsPage from './pages/ProjectsPage'
import type { JSX } from 'react'

function RequireAuth({ children }: { children: JSX.Element }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="container">불러오는 중…</div>
  if (!user) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            element={
              <RequireAuth>
                <Layout />
              </RequireAuth>
            }
          >
            <Route path="/" element={<ProjectsPage />} />
            <Route path="/projects/:id" element={<ProjectWorkspace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
