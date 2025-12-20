import { test, expect } from '@playwright/test';
import { getUserSettingsFromLocalStore } from '../../utils/utils';
import { SettingsPage } from '../../pages/settings-page';
import { DashboardPage } from '../../pages/dashboard-page';
import { ensureWeAreSignedIn } from '../../utils/utils';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  APPT_BROWSER_STORE_START_WEEK_MON,
  APPT_BROWSER_STORE_START_WEEK_SUN,
  APPT_START_OF_WEEK_MON,
  APPT_START_OF_WEEK_SUN,
 } from '../../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('settings - start of week on desktop browser', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    await ensureWeAreSignedIn(page);
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);

    // // navigate to the settings page, preferences section
    await settingsPage.gotoPreferencesSettings();
  });

  test('able to change start of week on desktop browser', async ({ page }) => {
    // change start of week to Monday and verify
    await settingsPage.changeStartOfWeekSetting(APPT_START_OF_WEEK_MON);

    // verify setting saved in browser local storage
    let localStore = await getUserSettingsFromLocalStore(page);
    expect.soft(localStore['startOfWeek']).toBe(APPT_BROWSER_STORE_START_WEEK_MON);

    // currently start of week setting doesn't actually change the dashboard calendar (see issue 1295)

    // change start of week back to Sunday
    await settingsPage.gotoPreferencesSettings();
    await settingsPage.changeStartOfWeekSetting(APPT_START_OF_WEEK_SUN);

    // verify setting saved in browser local storage
    localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['startOfWeek']).toBe(APPT_BROWSER_STORE_START_WEEK_SUN);
  });
});
