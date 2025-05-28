import { test, expect } from '@playwright/test';
import { navigateToAppointmentAndSignIn, getUserSettingsFromLocalStore, setDefaultUserSettingsLocalStore } from '../utils/utils';
import { SettingsPage } from '../pages/settings-page';
import { DashboardPage } from '../pages/dashboard-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  PLAYWRIGHT_TAG_PROD_NIGHTLY_MOBILE,
  TIMEOUT_3_SECONDS,
  APPT_BROWSER_STORE_12HR_TIME,
  APPT_BROWSER_STORE_24HR_TIME,
 } from '../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('general settings - time format', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY, PLAYWRIGHT_TAG_PROD_NIGHTLY_MOBILE],
}, () => {
  test.beforeEach(async ({ page }) => {
    // navigate to and sign into appointment
    await navigateToAppointmentAndSignIn(page);
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);

    // navigate to the general settings page
    await settingsPage.gotoGeneralSettingsPage();

    // ensure our settings are set to what the tests expect as default (in case a
    // previous test run failed and left the settings in an incorrect state)
    await setDefaultUserSettingsLocalStore(page);
    await page.reload();
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
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
