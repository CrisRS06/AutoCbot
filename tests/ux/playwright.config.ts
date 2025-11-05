import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright Configuration for AutoCbot UX/Frontend Tests
 * Focus: User experience, interactive elements, loading states, error handling
 */
export default defineConfig({
  testDir: './',

  // Run tests in parallel
  fullyParallel: true,

  // Fail the build on CI if you accidentally left test.only
  forbidOnly: !!process.env.CI,

  // Retry on CI only
  retries: process.env.CI ? 2 : 0,

  // Workers: parallel test execution
  workers: process.env.CI ? 1 : undefined,

  // Reporter: detailed HTML report
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list'],
    ['json', { outputFile: 'test-results.json' }]
  ],

  use: {
    // Base URL for tests
    baseURL: 'http://localhost:3000',

    // Collect trace on first retry
    trace: 'on-first-retry',

    // Screenshot on failure
    screenshot: 'only-on-failure',

    // Video on failure
    video: 'retain-on-failure',

    // Timeout for actions (click, fill, etc.)
    actionTimeout: 10000,

    // Navigation timeout
    navigationTimeout: 30000,
  },

  // Test timeout
  timeout: 60000,

  // Global setup/teardown
  // globalSetup: require.resolve('./helpers/global-setup.ts'),
  // globalTeardown: require.resolve('./helpers/global-teardown.ts'),

  // Projects for different browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    // Uncomment for cross-browser testing
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },

    // Mobile viewports
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  // Web server: start frontend before tests
  webServer: {
    command: 'cd ../../frontend && npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
