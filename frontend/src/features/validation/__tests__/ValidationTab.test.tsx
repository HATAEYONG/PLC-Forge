import { render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import ValidationTab from '../ValidationTab'

function mockFindings(results: unknown[]) {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ count: results.length, results }),
    }),
  )
}

describe('ValidationTab', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('CRITICAL Finding이 있으면 차단 경고를 표시한다', async () => {
    mockFindings([
      {
        id: '1',
        severity: 'CRITICAL',
        code: 'INTERLOCK_COVERAGE',
        title: '인터록 커버리지 부족',
        description: '',
        recommended_action: '',
        status: 'OPEN',
      },
    ])
    render(<ValidationTab projectId="p1" />)
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument())
    expect(screen.getByRole('alert')).toHaveTextContent('차단')
    expect(screen.getByText('인터록 커버리지 부족')).toBeInTheDocument()
  })

  it('Finding이 없으면 안내 문구를 표시한다', async () => {
    mockFindings([])
    render(<ValidationTab projectId="p1" />)
    await waitFor(() => expect(screen.getByText('검증을 실행하세요.')).toBeInTheDocument())
  })
})
