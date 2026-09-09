import { test, expect } from '@playwright/test';
import { SettingsPage } from '../pages/settings-page';
import {
  ensureWeAreSignedIn,
  getTestPlatform,
  getUserSettingsFromLocalStore,
  mobileSignInAndSetup,
} from '../utils/utils';

import {
  APPT_BROWSER_STORE_START_WEEK_MON,
  APPT_BROWSER_STORE_START_WEEK_SUN,
  APPT_START_OF_WEEK_MON,
  APPT_START_OF_WEEK_SUN,
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_E2E_SUITE_MOBILE,
  PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  TIMEOUT_3_SECONDS,
  TIMEOUT_60_SECONDS,
} from '../const/constants';

let settingsPage: SettingsPage;

test.describe('settings - start of week', {
  // Preserve the union of the former desktop and mobile tags so the common
  // source continues to run in regular and nightly suites on both platforms.
  tag: [
    PLAYWRIGHT_TAG_E2E_SUITE,
    PLAYWRIGHT_TAG_PROD_NIGHTLY,
    PLAYWRIGHT_TAG_E2E_SUITE_MOBILE,
    PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY,
  ],
}, () => {
  // BrowserStack iOS must complete mobile authentication/setup and two saved
  // start-of-week transitions. Give this stateful spec the same five-minute
  // budget as the consolidated language test, including its beforeEach work.
  test.setTimeout(5 * TIMEOUT_60_SECONDS);

  test.beforeEach(async ({ page }, testInfo) => {
    const projectName = testInfo.project.name;
    const testPlatform = getTestPlatform(projectName);

    // Pass the exact project name to SettingsPage so its scrolling helper
    // avoids unsupported scrollIntoViewIfNeeded calls on BrowserStack iOS.
    settingsPage = new SettingsPage(page, projectName);

    if (testPlatform === 'desktop') {
      // Desktop projects reuse the auth state prepared by auth.desktop.setup.ts
      // and revalidate it in case a long suite allowed the session to expire.
      await ensureWeAreSignedIn(page);
    } else {
      // Mobile projects cannot load the saved desktop storage state, so they
      // must sign in and restore the expected default settings for every test.
      await mobileSignInAndSetup(page, projectName);
    }

    await settingsPage.gotoPreferencesSettings();

    if (testPlatform !== 'desktop') {
      // Preserve the additional settling time required by BrowserStack mobile
      // devices after opening the Preferences section.
      await page.waitForTimeout(TIMEOUT_3_SECONDS);
    }
  });

  test.afterEach(async ({ page }, testInfo) => {
    // Close mobile pages so they do not remain open as tabs on BrowserStack.
    // Desktop fixtures manage their own page lifetime.
    if (getTestPlatform(testInfo.project.name) !== 'desktop') {
      await page.close();
    }
  });

  test('able to change start of week', async ({ page }, testInfo) => {
    const testPlatform = getTestPlatform(testInfo.project.name);

    // Change the setting to Monday and verify the persisted browser-store
    // value. Keep this assertion soft so the test still restores Sunday if
    // the intermediate verification fails.
    await settingsPage.changeStartOfWeekSetting(APPT_START_OF_WEEK_MON);
    let localStore = await getUserSettingsFromLocalStore(page);
    expect.soft(localStore['startOfWeek']).toBe(APPT_BROWSER_STORE_START_WEEK_MON);

    // The setting currently does not update the dashboard calendar itself
    // (issue 1295), so this test intentionally verifies persisted state only.

    if (testPlatform !== 'desktop') {
      // Preserve the mobile delay before reloading Preferences for restoration.
      await page.waitForTimeout(TIMEOUT_3_SECONDS);
    }
    await settingsPage.gotoPreferencesSettings();

    // Always restore Sunday so this stateful test does not affect subsequent
    // specs, then use a hard assertion to confirm restoration succeeded.
    await settingsPage.changeStartOfWeekSetting(APPT_START_OF_WEEK_SUN);
    localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['startOfWeek']).toBe(APPT_BROWSER_STORE_START_WEEK_SUN);
  });

  test.afterAll(async ({ browser }, testInfo) => {
    const projectName = testInfo.project.name;
    const testPlatform = getTestPlatform(projectName);
    const isLocalMobileView = projectName.toLowerCase().includes('view');

    // Close BrowserStack real-device sessions after this spec. Closing the
    // browser for the local `*-View` project breaks later emulated-mobile tests.
    if (testPlatform !== 'desktop' && !isLocalMobileView) {
      await browser.close();
    }
  });
});
