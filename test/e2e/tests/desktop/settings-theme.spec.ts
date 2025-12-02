import { test, expect } from '@playwright/test';
import { getUserSettingsFromLocalStore } from '../../utils/utils';
import { SettingsPage } from '../../pages/settings-page';
import { DashboardPage } from '../../pages/dashboard-page';
import { ensureWeAreSignedIn } from '../../utils/utils';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  APPT_THEME_SETTING_DARK,
  APPT_THEME_SETTING_LIGHT,
  APPT_BROWSER_STORE_THEME_LIGHT,
  APPT_BROWSER_STORE_THEME_DARK,
 } from '../../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('settings - theme on desktop browser', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    await ensureWeAreSignedIn(page);
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);

    // navigate to the settings page, preferences section
    await settingsPage.gotoPreferencesSettings();
  });

  test('able to change theme on desktop browser', async ({ page }) => {
    // change theme setting to dark mode and verify
    await settingsPage.changeThemeSetting(APPT_THEME_SETTING_DARK);
    expect(await settingsPage.isDarkModeEnabled(page)).toBeTruthy();

    // verify setting saved in browser local storage
    let localStore = await getUserSettingsFromLocalStore(page);
    expect.soft(localStore['colourScheme']).toBe(APPT_BROWSER_STORE_THEME_DARK);

    // change theme setting back to light mode and verify
    await settingsPage.changeThemeSetting(APPT_THEME_SETTING_LIGHT);
    expect(await settingsPage.isDarkModeEnabled(page)).toBeFalsy();
  
    // verify setting saved in browser local storage
    localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['colourScheme']).toBe(APPT_BROWSER_STORE_THEME_LIGHT);
  });
});
