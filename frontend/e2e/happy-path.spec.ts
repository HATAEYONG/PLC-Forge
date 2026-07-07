import { expect, test } from '@playwright/test'

const API = process.env.E2E_API_BASE ?? 'http://127.0.0.1:8000/api'
const ADMIN = { username: 'admin', password: 'admin1234!' }

/**
 * MVP 해피패스 (PRD §31 E2E): 로그인 → 프로젝트 → 인터뷰 → 설계 생성 →
 * 검증 → 승인 → Excel Export.
 *
 * 인터뷰 답변은 API로 시드해 결정론적으로 만들고, UI로 설계·검증·승인·Export를 검증한다.
 */
test('로그인부터 Export까지 해피패스', async ({ page, request }) => {
  // 1) 관리자 토큰 + 설계 착수 가능한 프로젝트 시드
  const tokenRes = await request.post(`${API}/auth/token/`, { data: ADMIN })
  const access = (await tokenRes.json()).access as string
  const headers = { Authorization: `Bearer ${access}`, 'Content-Type': 'application/json' }

  const company = await (
    await request.post(`${API}/companies/`, {
      headers,
      data: { name: `E2E-${Date.now()}`, industry: '식품' },
    })
  ).json()
  const code = `E2E-${Date.now().toString().slice(-6)}`
  const project = await (
    await request.post(`${API}/projects/`, {
      headers,
      data: { company: company.id, name: 'E2E 라인', code },
    })
  ).json()

  const facts: [string, unknown, string][] = [
    ['DEVICE_LIST', ['펌프', '히터'], 'LIST'],
    ['MEASUREMENT_REQUIREMENTS', ['LEVEL', 'TEMPERATURE'], 'LIST'],
    ['CONTINUOUS_LEVEL_REQUIRED', true, 'BOOLEAN'],
    ['STEAM_PRESENT_DURING_CIP', true, 'BOOLEAN'],
    ['ESTOP_REQUIRED', true, 'BOOLEAN'],
    ['HMI_REQUIRED', true, 'BOOLEAN'],
    ['CONTROL_MODE', 'AUTO', 'STRING'],
  ]
  for (const [k, v, t] of facts) {
    await request.post(`${API}/facts/`, {
      headers,
      data: { project: project.id, fact_key: k, value_json: v, value_type: t, source_type: 'MANUAL' },
    })
  }

  // 2) 로그인 UI
  await page.goto('/login')
  await page.fill('#username', ADMIN.username)
  await page.fill('#password', ADMIN.password)
  await page.click('button[type=submit]')
  await page.waitForURL('/')

  // 3) 워크스페이스 → 인터뷰 탭 렌더
  await page.goto(`/projects/${project.id}`)
  await expect(page.getByRole('button', { name: '인터뷰' })).toBeVisible()

  // 4) 설계 생성
  await page.getByRole('button', { name: '설계' }).click()
  await page.getByRole('button', { name: '규칙 적용 + 설계 생성' }).click()
  await expect(page.getByText('센서 요구사항', { exact: false })).toBeVisible({ timeout: 15_000 })
  await expect(page.getByText('PLC Sizing', { exact: false })).toBeVisible()

  // 5) 검증 (인터록 materialize됨 → CRITICAL 0)
  await page.getByRole('button', { name: '검증' }).click()
  await page.getByRole('button', { name: '검증 실행' }).click()
  await expect(page.locator('span.badge.CRITICAL').first()).toHaveText(/CRITICAL 0/, {
    timeout: 10_000,
  })

  // 6) 승인 (센서 설계)
  await page.getByRole('button', { name: '승인' }).click()
  await page.selectOption('select', 'SENSOR_DESIGN')
  await page.getByRole('button', { name: '검토 제출' }).click()
  await page.locator('table button', { hasText: '승인' }).first().click()
  await expect(page.locator('td span.badge', { hasText: 'APPROVED' })).toBeVisible({
    timeout: 10_000,
  })

  // 7) Excel Export 다운로드
  await page.getByRole('button', { name: '설계' }).click()
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.getByRole('button', { name: 'Excel Export', exact: false }).click(),
  ])
  expect(download.suggestedFilename()).toContain('.xlsx')
})
