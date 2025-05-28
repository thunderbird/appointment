import { test, expect } from '@playwright/test';
import { navigateToAppointmentAndSignIn, getUserSettingsFromLocalStore, setDefaultUserSettingsLocalStore } from '../utils/utils';
import { SettingsPage } from '../pages/settings-page';
import { DashboardPage } from '../pages/dashboard-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  PLAYWRIGHT_TAG_PROD_NIGHTLY_MOBILE,
  TIMEOUT_3_SECONDS,
  APPT_BROWSER_STORE_START_WEEK_MON,
  APPT_BROWSER_STORE_START_WEEK_SUN,
  APPT_START_OF_WEEK_MON,
  APPT_START_OF_WEEK_SUN,
  APPT_START_OF_WEEK_DASHBOARD_MON,
  APPT_START_OF_WEEK_DASHBOARD_SUN,
 } from '../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('general settings - start of week', {
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

  test('able to change start of week', async ({ page }) => {
    // change start of week to Monday and verify
    await settingsPage.changeStartOfWeekSetting(APPT_START_OF_WEEK_MON);

    // verify setting saved in browser local storage
    await settingsPage.gotoGeneralSettingsPage();
    let localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['startOfWeek']).toBe(APPT_BROWSER_STORE_START_WEEK_MON);

    // verify on dashboard
    await dashboardPage.gotoToDashboardMonthView();
    var firstDayOfWeekText = await dashboardPage.firstDayOfWeekMonthView.innerText();
    expect(firstDayOfWeekText).toEqual(APPT_START_OF_WEEK_DASHBOARD_MON);

    // change start of week back to Sunday and verify
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
    await settingsPage.gotoGeneralSettingsPage();
    await settingsPage.changeStartOfWeekSetting(APPT_START_OF_WEEK_SUN);

    // verify setting saved in browser local storage
    await settingsPage.gotoGeneralSettingsPage();
    localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['startOfWeek']).toBe(APPT_BROWSER_STORE_START_WEEK_SUN);

    // verify on dashboard
    await dashboardPage.gotoToDashboardMonthView();
    firstDayOfWeekText = await dashboardPage.firstDayOfWeekMonthView.innerText();
    expect(firstDayOfWeekText).toEqual(APPT_START_OF_WEEK_DASHBOARD_SUN);
  });
});
