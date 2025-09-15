import { test, expect } from '@playwright/test';
import { mobileSignInAndSetup, getUserSettingsFromLocalStore } from '../../utils/utils';
import { SettingsPage } from '../../pages/settings-page';
import { DashboardPage } from '../../pages/dashboard-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE_MOBILE,
  PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY,
  APPT_THEME_SETTING_DARK,
  APPT_THEME_SETTING_LIGHT,
  APPT_BROWSER_STORE_THEME_LIGHT,
  APPT_BROWSER_STORE_THEME_DARK,
  TIMEOUT_3_SECONDS,
 } from '../../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('settings - theme on mobile browser', {
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

  test('able to change theme on mobile browser', async ({ page }) => {
    // change theme setting to dark mode and verify
    await settingsPage.changeThemeSetting(APPT_THEME_SETTING_DARK);
    // can take a bit of extra time on mobile/view emulator to update theme
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
    expect(await settingsPage.isDarkModeEnabled(page)).toBeTruthy();

    // verify setting saved in browser local storage
    let localStore = await getUserSettingsFromLocalStore(page);
    expect.soft(localStore['colourScheme']).toBe(APPT_BROWSER_STORE_THEME_DARK);

    // change theme setting back to light mode and verify
    await settingsPage.changeThemeSetting(APPT_THEME_SETTING_LIGHT);
    // can take a bit of extra time on mobile/view emulator to update theme
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
    expect(await settingsPage.isDarkModeEnabled(page)).toBeFalsy();
  
    // verify setting saved in browser local storage
    localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['colourScheme']).toBe(APPT_BROWSER_STORE_THEME_LIGHT);
  });
});
