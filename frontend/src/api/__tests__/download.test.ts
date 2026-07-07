import { afterEach, describe, expect, it, vi } from 'vitest'
import { downloadFile } from '../download'

describe('downloadFile', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('응답 파일명으로 다운로드 링크를 트리거한다', async () => {
    const blob = new Blob(['x'], { type: 'application/octet-stream' })
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        headers: { get: () => 'attachment; filename="PLC-Forge_ABC.xlsx"' },
        blob: () => Promise.resolve(blob),
      }),
    )
    vi.stubGlobal('URL', {
      createObjectURL: vi.fn(() => 'blob:x'),
      revokeObjectURL: vi.fn(),
    })
    const click = vi.fn()
    const anchor = {
      href: '',
      download: '',
      click,
      remove: vi.fn(),
    } as unknown as HTMLAnchorElement
    vi.spyOn(document, 'createElement').mockReturnValue(anchor)
    vi.spyOn(document.body, 'appendChild').mockImplementation(() => anchor)

    await downloadFile('/api/projects/1/export/', 'fallback.xlsx')
    expect(click).toHaveBeenCalled()
    expect(anchor.download).toBe('PLC-Forge_ABC.xlsx')
  })

  it('오류 응답은 ApiRequestError로 던진다', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        headers: { get: () => null },
        json: () =>
          Promise.resolve({ error: { code: 'not_found', message: '없음', details: null } }),
      }),
    )
    await expect(downloadFile('/x', 'f.xlsx')).rejects.toMatchObject({ code: 'not_found' })
  })
})
