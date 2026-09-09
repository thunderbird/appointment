import { test, expect } from '@playwright/test';
import { SettingsPage } from '../pages/settings-page';
import {
  ensureWeAreSignedIn,
  getTestPlatform,
  getUserSettingsFromLocalStore,
  mobileSignInAndSetup,
} from '../utils/utils';

import {
  APPT_BROWSER_STORE_LANGUAGE_DE,
  APPT_BROWSER_STORE_LANGUAGE_EN,
  APPT_LANGUAGE_SETTING_DE,
  APPT_LANGUAGE_SETTING_EN,
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_E2E_SUITE_MOBILE,
  PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  TIMEOUT_3_SECONDS,
  TIMEOUT_30_SECONDS,
  TIMEOUT_60_SECONDS,
} from '../const/constants';

let settingsPage: SettingsPage;

test.describe('settings - language', {
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
  // language transitions. The suite-wide 150-second limit can expire even
  // when those operations are succeeding, so give this stateful spec a
  // five-minute budget that includes its beforeEach work.
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

  test('able to change language', async ({ page }) => {
    // Change English to German. These assertions are soft so the test still
    // reaches the restoration steps if a German UI assertion fails; the soft
    // failure is retained and will still fail the completed test.
    await settingsPage.changeLanguageSetting(APPT_LANGUAGE_SETTING_EN, APPT_LANGUAGE_SETTING_DE);
    await expect.soft(settingsPage.settingsHeaderDE).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await expect.soft(settingsPage.preferencesHeaderDE).toBeVisible();

    let localStore = await getUserSettingsFromLocalStore(page);
    expect.soft(localStore['language']).toBe(APPT_BROWSER_STORE_LANGUAGE_DE);

    // Always restore English so this stateful test does not affect subsequent
    // specs. Once the UI is English again, use hard assertions for restoration.
    await settingsPage.changeLanguageSetting(APPT_LANGUAGE_SETTING_DE, APPT_LANGUAGE_SETTING_EN);
    await expect(settingsPage.settingsHeaderEN).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await expect(settingsPage.preferencesHeaderEN).toBeVisible();

    localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['language']).toBe(APPT_BROWSER_STORE_LANGUAGE_EN);
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
