import { defineConfig, devices } from '@playwright/test';

/**
 * Read environment variables from file.
 * https://github.com/motdotla/dotenv
 */
import dotenv from 'dotenv';
import path from 'path';
dotenv.config({ path: path.resolve(__dirname, '.env') });

/**
 * See https://playwright.dev/docs/test-configuration.
 */
export default defineConfig({
  testDir: './tests',
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 1 : 0,
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : 1, // actualy don't run in parallel locally either, for now
  // Global timeout: Playwright will timeout if the entire session (includes all test runs) exceeds this.
  // Must take into account running on mulitple browsers (and BrowserStack is much slower too!). Odds are the
  // tests will time out at the locator/test level first anyway; but there is no default so best to specify
  globalTimeout: 12 * 60 * 1000,
  // Individual test timeout - a single test will time out if it is still running after this time (ms)
  timeout:  150 * 1000, // 2.5 minutes
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  // When running in CI we don't use the html report as we use BrowserStack's reporting
  reporter: process.env.CI ? [['list']] : [['html']] ,
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    // baseURL: 'http://127.0.0.1:3000',
    trace: 'off', // traces can contain sensitive info so only do this manually locally if need be
    screenshot: 'only-on-failure',
    // Maximum time (ms) each action such as `click()` can take. Defaults to 0 (no limit)
    actionTimeout: 10_000,
    // Maximum time given for browser page navigation
    navigationTimeout: 15_000,
  },
  expect: {
    // set default timeout for all expects that have a {timeout} option i.e. if locators are not found,
    // timeout after 10 seconds instead of waiting for the entire test timeout set above
    timeout: 10_000,
  },

  /* Configure projects for major browsers */
  projects: [
    // Setup project - signs into Appointment once for all the tests
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // Use prepared auth state
        storageState: 'test-results/.auth/user.json',
       },
      dependencies: ['setup'],
    },

    {
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
        // Use prepared auth state
        storageState: 'test-results/.auth/user.json',
       },
      dependencies: ['setup'],
    },

    //{
    //  name: 'webkit',
    //  use: { ...devices['Desktop Safari'] },
    //},

    /* Test against mobile viewports. */
    // {
    //   name: 'Mobile Chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
    // {
    //   name: 'Mobile Safari',
    //   use: { ...devices['iPhone 12'] },
    // },

    /* Test against branded browsers. */
    // {
    //   name: 'Microsoft Edge',
    //   use: { ...devices['Desktop Edge'], channel: 'msedge' },
    // },
    // {
    //   name: 'Google Chrome',
    //   use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    // },
  ],

  /* Run your local dev server before starting the tests */
  // webServer: {
  //   command: 'npm run start',
  //   url: 'http://127.0.0.1:3000',
  //   reuseExistingServer: !process.env.CI,
  // },
});
