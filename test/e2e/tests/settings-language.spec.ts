import { test, expect } from '@playwright/test';
import { getUserSettingsFromLocalStore } from '../utils/utils';
import { SettingsPage } from '../pages/settings-page';
import { DashboardPage } from '../pages/dashboard-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  APPT_LANGUAGE_SETTING_DE,
  APPT_LANGUAGE_SETTING_EN,
  TIMEOUT_30_SECONDS,
  APPT_BROWSER_STORE_LANGUAGE_EN,
  APPT_BROWSER_STORE_LANGUAGE_DE,
 } from '../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('settings - language', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    // note: we are already signed into Appointment with our default settings (via our auth-setup)
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);

    // navigate to the settings page, preferences section
    await settingsPage.gotoPreferencesSettings();
  });

  test('able to change language', async ({ page }) => {
    // change language setting to DE and verify; we use expect.soft here because if the expect fails
    // we still want the test to continue so that the test will change the setting back to original value
    await settingsPage.changeLanguageSetting(APPT_LANGUAGE_SETTING_EN, APPT_LANGUAGE_SETTING_DE);
    await expect.soft(settingsPage.settingsHeaderDE).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await expect.soft(settingsPage.preferencesHeaderDE).toBeVisible();

    // verify setting saved in browser local storage
    let localStore = await getUserSettingsFromLocalStore(page);
    expect.soft(localStore['language']).toBe(APPT_BROWSER_STORE_LANGUAGE_DE);

    // change language settings back to EN and verify
    await settingsPage.changeLanguageSetting(APPT_LANGUAGE_SETTING_DE, APPT_LANGUAGE_SETTING_EN);
    await expect(settingsPage.settingsHeaderEN).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await expect(settingsPage.preferencesHeaderEN).toBeVisible();

    // verify setting saved in browser local storage
    localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['language']).toBe(APPT_BROWSER_STORE_LANGUAGE_EN);
  });
});
