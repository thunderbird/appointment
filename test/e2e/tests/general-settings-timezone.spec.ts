import { test, expect } from '@playwright/test';
import { getUserSettingsFromLocalStore } from '../utils/utils';
import { SettingsPage } from '../pages/settings-page';
import { DashboardPage } from '../pages/dashboard-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  APPT_TIMEZONE_SETTING_PRIMARY,
  APPT_TIMEZONE_SETTING_HALIFAX,
  TIMEOUT_2_SECONDS,
 } from '../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('general settings - timezone', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    // note: we are already signed into Appointment with our default settings (via our auth-setup)
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);

    // navigate to the general settings page
    await settingsPage.gotoGeneralSettingsPage();
  });

  test('able to change timezone', async ({ page }) => {
    // change time zone setting
    await settingsPage.timeZoneSelect.scrollIntoViewIfNeeded();
    await page.waitForTimeout(TIMEOUT_2_SECONDS);
    await settingsPage.changeTimezoneSetting(APPT_TIMEZONE_SETTING_HALIFAX);

    // verify setting saved in browser local storage
    let localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['timezone']).toBe(APPT_TIMEZONE_SETTING_HALIFAX);

    // change time format setting back
    await settingsPage.gotoGeneralSettingsPage();
    await settingsPage.timeZoneSelect.scrollIntoViewIfNeeded();
    await page.waitForTimeout(TIMEOUT_2_SECONDS);
    await settingsPage.changeTimezoneSetting(APPT_TIMEZONE_SETTING_PRIMARY);

    // verify setting saved in browser local storage
    localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['timezone']).toBe(APPT_TIMEZONE_SETTING_PRIMARY);
  });
});