import { render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import ApprovalTab from '../ApprovalTab'

describe('ApprovalTab', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('IN_REVIEW 승인은 승인/반려 버튼을 노출한다', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: () =>
          Promise.resolve({
            count: 1,
            results: [
              { id: 'a1', target: 'SENSOR_DESIGN', status: 'IN_REVIEW', reason: '', history: [] },
            ],
          }),
      }),
    )
    render(<ApprovalTab projectId="p1" />)
    await waitFor(() => expect(screen.getByText('승인')).toBeInTheDocument())
    expect(screen.getByText('반려')).toBeInTheDocument()
    // select 옵션과 테이블 셀에 동일 라벨이 있으므로 셀(td) 기준으로 확인
    const cell = screen.getByRole('cell', { name: '센서 설계' })
    expect(cell).toBeInTheDocument()
  })
})
