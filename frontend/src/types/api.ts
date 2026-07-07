/** 백엔드 통일 오류 응답 형식 (PRD §33-19) */
export interface ApiError {
  error: {
    code: string
    message: string
    details: unknown
  }
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface HealthResponse {
  status: 'ok' | 'degraded'
  db: boolean
  version: string
}
