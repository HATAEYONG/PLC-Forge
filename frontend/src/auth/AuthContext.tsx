import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import { api, clearTokens, getToken, setTokens } from '../api/client'
import type { User } from '../types/domain'

interface AuthState {
  user: User | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthState | null>(null)

interface TokenResponse {
  access: string
  refresh: string
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const loadUser = useCallback(async () => {
    if (!getToken()) {
      setLoading(false)
      return
    }
    try {
      setUser(await api.get<User>('/api/auth/me/'))
    } catch {
      clearTokens()
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadUser()
  }, [loadUser])

  const login = useCallback(async (username: string, password: string) => {
    const tokens = await api.post<TokenResponse>('/api/auth/token/', { username, password })
    setTokens(tokens.access, tokens.refresh)
    setUser(await api.get<User>('/api/auth/me/'))
  }, [])

  const logout = useCallback(() => {
    clearTokens()
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>{children}</AuthContext.Provider>
  )
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
