import { render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { HealthStatus } from '../HealthStatus'

function mockFetchOnce(body: unknown, ok = true, status = 200) {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok,
      status,
      json: () => Promise.resolve(body),
    }),
  )
}

describe('HealthStatus', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('백엔드 상태를 표시한다', async () => {
    mockFetchOnce({ status: 'ok', db: true, version: '0.1.0' })
    render(<HealthStatus />)
    expect(await screen.findByText('ok')).toBeInTheDocument()
    expect(screen.getByText(/DB 연결됨/)).toBeInTheDocument()
  })

  it('오류 시 통일 오류 형식의 메시지를 표시한다', async () => {
    mockFetchOnce(
      { error: { code: 'error', message: '서비스를 사용할 수 없습니다.', details: null } },
      false,
      503,
    )
    render(<HealthStatus />)
    expect(await screen.findByRole('alert')).toHaveTextContent('서비스를 사용할 수 없습니다.')
  })
})
