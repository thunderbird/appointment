import { test, expect } from '@playwright/test';
import { SettingsPage } from '../pages/settings-page';
import { DashboardPage } from '../pages/dashboard-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  APPT_TARGET_ENV,
  TIMEOUT_30_SECONDS,
 } from '../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('connected accounts settings', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    // note: we are already signed into Appointment with our default settings (via our auth-setup)
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);
    // navigate to the connected accounts settings page
    await settingsPage.gotoConnectedAccountsSettingsPage();
  });

  test('edit profile button', async ({ page }) => {
    // verify that clicking the `edit profile` button redirects to the Mozilla Account profile page
    // note that on dev env this relies on having VITE_FXA_EDIT_PROFILE= set to point to stage FxA
    // skip this on dev env because stage FxA use may or may not be setup to use with local dev
    if (APPT_TARGET_ENV !== 'dev') {
      await settingsPage.editProfileBtn.click();
      await expect(settingsPage.mozProfilePageLogo).toBeVisible( { timeout: TIMEOUT_30_SECONDS });
      await expect(settingsPage.mozProfileSettingsSection).toBeVisible();
    }
  });

  test('disconnect calendar button', async ({ page }) => {
    // verify that clicking the google calendar `disconnect` button brings up a confirmation dialog
    // just cancel out; we don't want to actually disconnect the calendar and break the tests
    await settingsPage.disconnectGoogleCalendarBtn.click();
    await settingsPage.disconnectGoogleCalendarBackBtn.click();
  });

  test('connect caldav connection dialog', async ({ page }) => {
    // verify that clicking the caldav connection `connect` button brings up the caldav connection dialog
    await settingsPage.connectCaldavBtn.click();
    await expect(settingsPage.addCaldavConnectionUsernameInput).toBeEditable();
    await expect(settingsPage.addCaldavConnectionLocationInput).toBeEditable();
    await expect(settingsPage.addCaldavConnectionPasswordInput).toBeEditable();
    await settingsPage.addCaldavConnectionCloseModalBtn.click();
  });
});
