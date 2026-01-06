import { test, expect } from '@playwright/test';
import { mobileSignInAndSetup, getUserSettingsFromLocalStore } from '../../utils/utils';
import { SettingsPage } from '../../pages/settings-page';
import { DashboardPage } from '../../pages/dashboard-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE_MOBILE,
  PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY,
  APPT_START_OF_WEEK_MON,
  APPT_START_OF_WEEK_SUN,
  APPT_BROWSER_STORE_START_WEEK_MON,
  APPT_BROWSER_STORE_START_WEEK_SUN,
  TIMEOUT_3_SECONDS,
 } from '../../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('settings - start of week on mobile browser', {
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

  test('able to change start of week on mobile browser', async ({ page }) => {
    // change start of week to Monday and verify
    await settingsPage.changeStartOfWeekSetting(APPT_START_OF_WEEK_MON);

    // verify setting saved in browser local storage
    let localStore = await getUserSettingsFromLocalStore(page);
    expect.soft(localStore['startOfWeek']).toBe(APPT_BROWSER_STORE_START_WEEK_MON);

    // currently start of week setting doesn't actually change the dashboard calendar (see issue 1295)

    // change start of week back to Sunday and verify
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
    await settingsPage.gotoPreferencesSettings();
    await settingsPage.changeStartOfWeekSetting(APPT_START_OF_WEEK_SUN);

    // verify setting saved in browser local storage
    localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['startOfWeek']).toBe(APPT_BROWSER_STORE_START_WEEK_SUN);
  });

  test.afterAll(async ({ browser }, testInfo) => {
    // close the browser when we're done (good practice for BrowserStack); only do this for BrowserStack,
    // because if we do this when running on a local playwright mobile viewport the tests will fail
    if (!testInfo.project.name.includes('View')) {
      await browser.close();
    }
  });
});
