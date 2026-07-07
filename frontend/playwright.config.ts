import { defineConfig, devices } from '@playwright/test'

// PW_CHROMIUM이 지정되면(예: 사전설치 Chromium) 해당 실행 경로를 사용하고,
// 없으면(CI 등) Playwright가 설치한 기본 브라우저를 사용한다.
const CHROMIUM = process.env.PW_CHROMIUM
const BASE_URL = process.env.E2E_BASE_URL ?? 'http://127.0.0.1:5173'

const launchOptions = CHROMIUM
  ? { executablePath: CHROMIUM, args: ['--headless=new', '--no-sandbox'] }
  : { args: ['--no-sandbox'] }

export default defineConfig({
  testDir: './e2e',
  timeout: 60_000,
  fullyParallel: false,
  workers: 1,
  reporter: [['list']],
  use: {
    baseURL: BASE_URL,
    trace: 'off',
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        launchOptions,
      },
    },
  ],
})
