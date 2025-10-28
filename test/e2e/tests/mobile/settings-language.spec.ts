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

  test.beforeEach(async ({ page }) => {
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);

    // mobile browsers don't support saving auth storage state so must sign in before each test
    await mobileSignInAndSetup(page);

    // now navigate to the settings page, preferences section
    await settingsPage.gotoPreferencesSettings();
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
  });

  test.afterEach(async ({ page }) => {
    // close the current browser page so it won't interfere with next test
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
});
