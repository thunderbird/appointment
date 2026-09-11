import { test, expect } from '@playwright/test';
import { SettingsPage } from '../pages/settings-page';
import {
  ensureWeAreSignedIn,
  getTestPlatform,
  getUserSettingsFromLocalStore,
  mobileSignInAndSetup,
} from '../utils/utils';

import {
  APPT_BROWSER_STORE_THEME_DARK,
  APPT_BROWSER_STORE_THEME_LIGHT,
  APPT_THEME_SETTING_DARK,
  APPT_THEME_SETTING_LIGHT,
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_E2E_SUITE_MOBILE,
  PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  TIMEOUT_3_SECONDS,
  TIMEOUT_60_SECONDS,
} from '../const/constants';

let settingsPage: SettingsPage;

test.describe('settings - theme', {
  // Preserve the union of the former desktop and mobile tags so the common
  // source continues to run in regular and nightly suites on both platforms.
  tag: [
    PLAYWRIGHT_TAG_E2E_SUITE,
    PLAYWRIGHT_TAG_PROD_NIGHTLY,
    PLAYWRIGHT_TAG_E2E_SUITE_MOBILE,
    PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY,
  ],
}, () => {
  // BrowserStack mobile must complete authentication/setup and two persisted
  // theme transitions. Match the other stateful settings specs with a
  // five-minute budget that includes beforeEach work on slower production runs.
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

  test('able to change theme', async ({ page }, testInfo) => {
    const testPlatform = getTestPlatform(testInfo.project.name);

    // Change to dark mode and verify both the rendered theme and its persisted
    // browser-store value. Keep the store assertion soft so restoration runs.
    await settingsPage.changeThemeSetting(APPT_THEME_SETTING_DARK);
    if (testPlatform !== 'desktop') {
      // Theme application can lag behind the successful save on real mobile
      // devices and the local emulated viewport.
      await page.waitForTimeout(TIMEOUT_3_SECONDS);
    }
    expect(await settingsPage.isDarkModeEnabled(page)).toBeTruthy();

    let localStore = await getUserSettingsFromLocalStore(page);
    expect.soft(localStore['colourScheme']).toBe(APPT_BROWSER_STORE_THEME_DARK);

    // Always restore light mode so this stateful test does not affect later
    // specs, then use hard assertions to confirm restoration succeeded.
    await settingsPage.changeThemeSetting(APPT_THEME_SETTING_LIGHT);
    if (testPlatform !== 'desktop') {
      await page.waitForTimeout(TIMEOUT_3_SECONDS);
    }
    expect(await settingsPage.isDarkModeEnabled(page)).toBeFalsy();

    localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['colourScheme']).toBe(APPT_BROWSER_STORE_THEME_LIGHT);
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
