import type { ApiError } from '../types/api'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`)
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as ApiError | null
    throw new Error(body?.error?.message ?? `HTTP ${response.status}`)
  }
  return (await response.json()) as T
}
