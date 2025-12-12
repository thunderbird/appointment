import { test, expect } from '@playwright/test';
import { mobileSignInAndSetup, getUserSettingsFromLocalStore } from '../../utils/utils';
import { SettingsPage } from '../../pages/settings-page';
import { DashboardPage } from '../../pages/dashboard-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE_MOBILE,
  PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY,
  APPT_LANGUAGE_SETTING_EN,
  APPT_LANGUAGE_SETTING_DE,
  APPT_BROWSER_STORE_LANGUAGE_EN,
  APPT_BROWSER_STORE_LANGUAGE_DE,
  TIMEOUT_3_SECONDS,
  TIMEOUT_30_SECONDS,
 } from '../../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('settings - language on mobile browser', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE_MOBILE, PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY],
}, () => {

  test.beforeEach(async ({ page }, testInfo) => {
    settingsPage = new SettingsPage(page, testInfo.project.name); // i.e. 'ios-safari'
    dashboardPage = new DashboardPage(page);

    // mobile browsers don't support saving auth storage state so must sign in before each test
    // send in the playright test project name i.e. safari-ios because some mobile platforms differ
    await mobileSignInAndSetup(page, testInfo.project.name);

    // now navigate to the settings page, preferences section
    await settingsPage.gotoPreferencesSettings();
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
  });

  test.afterEach(async ({ page }) => {
    // close the browser page when we're done so it doesn't stay as a tab on mobile browser
    await page.close();
  });

  test('able to change language on mobile browser', async ({ page }) => {
    // change language setting to DE and verify; we use expect.soft here because if the expect fails
    // we still want the test to continue so that the test will change the setting back to original value
    await settingsPage.changeLanguageSetting(APPT_LANGUAGE_SETTING_EN, APPT_LANGUAGE_SETTING_DE);
    await expect.soft(settingsPage.settingsHeaderDE).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await expect.soft(settingsPage.preferencesHeaderDE).toBeVisible();

    // verify setting saved in browser local storage
    let localStore = await getUserSettingsFromLocalStore(page);
    expect.soft(localStore['language']).toBe(APPT_BROWSER_STORE_LANGUAGE_DE);

    // change language settings back to EN and verify; uses DE save changes button
    await settingsPage.changeLanguageSetting(APPT_LANGUAGE_SETTING_DE, APPT_LANGUAGE_SETTING_EN);
    await expect(settingsPage.settingsHeaderEN).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await expect(settingsPage.preferencesHeaderEN).toBeVisible();

    // verify setting saved in browser local storage
    localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['language']).toBe(APPT_BROWSER_STORE_LANGUAGE_EN);
  });

  test.afterAll(async ({ browser }) => {
    // close the browser when we're done, BrowserStack needs this or may report BROWSERSTACK_IDLE_TIMEOUT
    await browser.close();
  });
});
