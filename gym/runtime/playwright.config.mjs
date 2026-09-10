import { defineConfig } from '@playwright/test';
import path from 'node:path';
const root = process.env.OMAGYM_PROJECT;
export default defineConfig({
  testDir: root, testMatch: '**/challenge.spec.js', workers: 1, retries: 0,
  timeout: 12000, expect: { timeout: 1500 },
  outputDir: path.join(root, '.test-results'),
  reporter: [['json', { outputFile: path.join(root, '.test-report.json') }]],
  use: { baseURL: 'http://127.0.0.1:4399', browserName: 'chromium',
    launchOptions: { executablePath: '/usr/bin/chromium', args: ['--no-sandbox', '--disable-dev-shm-usage'] } },
  webServer: { command: `${process.execPath} ${path.join(import.meta.dirname, 'web-server.mjs')}`,
    url: 'http://127.0.0.1:4399', reuseExistingServer: false, timeout: 20000 },
});
