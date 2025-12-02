import { test, expect } from '@playwright/test';
import { getUserSettingsFromLocalStore, setDefaultUserSettingsLocalStore } from '../../utils/utils';
import { SettingsPage } from '../../pages/settings-page';
import { DashboardPage } from '../../pages/dashboard-page';
import { ensureWeAreSignedIn } from '../../utils/utils';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  APPT_TIMEZONE_SETTING_PRIMARY,
  APPT_TIMEZONE_SETTING_HALIFAX,
  TIMEOUT_2_SECONDS,
 } from '../../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('settings - timezone on desktop browser', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    await ensureWeAreSignedIn(page);
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);

    // navigate to the settings page, preferences section
    await settingsPage.gotoPreferencesSettings();
  });

  test('able to change default timezone on desktop browser', async ({ page }) => {
    // change default time zone setting
    await settingsPage.defaultTimeZoneSelect.scrollIntoViewIfNeeded();
    await page.waitForTimeout(TIMEOUT_2_SECONDS);
    await settingsPage.changeDefaultTimezoneSetting(APPT_TIMEZONE_SETTING_HALIFAX);

    // verify setting saved in browser local storage
    let localStore = await getUserSettingsFromLocalStore(page);
    expect.soft(localStore['timezone']).toBe(APPT_TIMEZONE_SETTING_HALIFAX);

    // change timzone setting back via local storage
    await setDefaultUserSettingsLocalStore(page);
    await page.waitForTimeout(TIMEOUT_2_SECONDS);

    // verify setting saved in browser local storage
    localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['timezone']).toBe(APPT_TIMEZONE_SETTING_PRIMARY);
  });
});
