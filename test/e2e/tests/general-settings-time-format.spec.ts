import { test, expect } from '@playwright/test';
import { getUserSettingsFromLocalStore } from '../utils/utils';
import { SettingsPage } from '../pages/settings-page';
import { DashboardPage } from '../pages/dashboard-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  TIMEOUT_3_SECONDS,
  APPT_BROWSER_STORE_12HR_TIME,
  APPT_BROWSER_STORE_24HR_TIME,
 } from '../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('general settings - time format', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY]
}, () => {
  test.beforeEach(async ({ page }) => {
    // note: we are already signed into Appointment with our default settings (via our auth-setup)
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);

    // navigate to the general settings page
    await settingsPage.gotoGeneralSettingsPage();
  });

  test('able to change time format', async ({ page }) => {
    // change time format setting to 24-hour format and verify
    await settingsPage.set24hrFormat();

    // verify setting saved in browser local storage
    await settingsPage.gotoGeneralSettingsPage();
    let localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['timeFormat']).toBe(APPT_BROWSER_STORE_24HR_TIME);

    // change time format setting back to 12-hour format
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
    await settingsPage.gotoGeneralSettingsPage();
    await settingsPage.set12hrFormat();

    // verify setting saved in browser local storage
    await settingsPage.gotoGeneralSettingsPage();
    localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['timeFormat']).toBe(APPT_BROWSER_STORE_12HR_TIME); 
  });
});
