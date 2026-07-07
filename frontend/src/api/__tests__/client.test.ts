import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiRequestError, api } from '../client'

function mockFetch(body: unknown, ok: boolean, status = 200) {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({ ok, status, json: () => Promise.resolve(body) }),
  )
}

describe('api client', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('성공 응답 본문을 반환한다', async () => {
    mockFetch({ id: '1' }, true)
    await expect(api.get('/x')).resolves.toEqual({ id: '1' })
  })

  it('통일 오류 포맷을 ApiRequestError로 변환한다', async () => {
    mockFetch(
      { error: { code: 'validation_error', message: '입력값 오류', details: { name: ['필수'] } } },
      false,
      400,
    )
    await expect(api.post('/x', {})).rejects.toMatchObject({
      code: 'validation_error',
      status: 400,
      message: '입력값 오류',
    })
  })

  it('ApiRequestError는 details를 보존한다', async () => {
    mockFetch({ error: { code: 'e', message: 'm', details: [1, 2] } }, false, 409)
    try {
      await api.get('/x')
      throw new Error('should have thrown')
    } catch (err) {
      expect(err).toBeInstanceOf(ApiRequestError)
      expect((err as ApiRequestError).details).toEqual([1, 2])
    }
  })
})
