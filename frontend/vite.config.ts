/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': process.env.VITE_PROXY_TARGET ?? 'http://127.0.0.1:8000',
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/setupTests.ts',
    // 단위 테스트는 src만. Playwright e2e는 `npm run e2e`로 별도 실행한다.
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
  },
})
