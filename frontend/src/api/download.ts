import { ApiRequestError, getToken } from './client'
import type { ApiError } from '../types/api'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

/** 인증 토큰을 포함해 바이너리 파일을 내려받아 브라우저 다운로드를 트리거한다. */
export async function downloadFile(path: string, fallbackName: string): Promise<void> {
  const token = getToken()
  const response = await fetch(`${API_BASE}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as ApiError | null
    throw new ApiRequestError(response.status, body, `HTTP ${response.status}`)
  }

  const disposition = response.headers.get('Content-Disposition') ?? ''
  const match = /filename="?([^"]+)"?/.exec(disposition)
  const filename = match?.[1] ?? fallbackName

  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}
