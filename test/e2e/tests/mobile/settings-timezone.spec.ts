import { test, expect } from '@playwright/test';
import { mobileSignInAndSetup, getUserSettingsFromLocalStore } from '../../utils/utils';
import { SettingsPage } from '../../pages/settings-page';
import { DashboardPage } from '../../pages/dashboard-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE_MOBILE,
  PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY,
  APPT_TIMEZONE_SETTING_HALIFAX,
  APPT_TIMEZONE_SETTING_PRIMARY,
  TIMEOUT_3_SECONDS,
 } from '../../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('settings - timezone on mobile browser', {
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
    // close the browser page when we're done so it doesn't stay as a tab on mobile browser
    await page.close();
  });

  test('able to change timezone on mobile browser', async ({ page }) => {
    // change default time zone setting
    await settingsPage.defaultTimeZoneSelect.scrollIntoViewIfNeeded();
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
    await settingsPage.changeDefaultTimezoneSetting(APPT_TIMEZONE_SETTING_HALIFAX);

    // verify setting saved in browser local storage
    let localStore = await getUserSettingsFromLocalStore(page);
    expect.soft(localStore['timezone']).toBe(APPT_TIMEZONE_SETTING_HALIFAX);

    // change time format setting back
    await settingsPage.gotoPreferencesSettings()
    await settingsPage.changeDefaultTimezoneSetting(APPT_TIMEZONE_SETTING_PRIMARY);

    // verify setting saved in browser local storage
    localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['timezone']).toBe(APPT_TIMEZONE_SETTING_PRIMARY);
  });
});
