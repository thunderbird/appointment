import { test, expect } from '@playwright/test';
import { navigateToAppointmentAndSignIn, setDefaultUserSettingsLocalStore } from '../utils/utils';
import { SettingsPage } from '../pages/settings-page';
import { DashboardPage } from '../pages/dashboard-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  PLAYWRIGHT_TAG_PROD_NIGHTLY_MOBILE,
  TIMEOUT_30_SECONDS,
 } from '../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('settings navigation', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY, PLAYWRIGHT_TAG_PROD_NIGHTLY_MOBILE],
}, () => {
  test.beforeEach(async ({ page }) => {
    // navigate to and sign into appointment
    await navigateToAppointmentAndSignIn(page);
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);

    // ensure our settings are set to what the tests expect as default (in case a
    // previous test run failed and left the settings in an incorrect state)
    await setDefaultUserSettingsLocalStore(page);
  });

  test('able to navigate through the settings panels', async ({ page }) => {
    // navigate to main settings URL and verify general settings displayed by default
    await settingsPage.gotoMainSettingsPage();
    await expect(settingsPage.settingsHeaderEN).toBeVisible({ timeout: TIMEOUT_30_SECONDS }); // generous time
    await expect(settingsPage.generalSettingsHeaderEN).toBeVisible({ timeout: TIMEOUT_30_SECONDS }); // generous time
    await expect(settingsPage.generalSettingsBtn).toBeEnabled();
    await expect(settingsPage.calendarSettingsBtn).toBeEnabled();
    await expect(settingsPage.accountSettingsBtn).toBeEnabled();
    await expect(settingsPage.connectedSettingsBtn).toBeEnabled();

    // click 'Calendar' button and verify corresponding settings appear
    await settingsPage.calendarSettingsBtn.click();
    await expect(settingsPage.calendarSettingsHeader).toBeVisible({ timeout: TIMEOUT_30_SECONDS }); // generous time

    // click 'Account' button and verify corresponding settings appear
    await settingsPage.accountSettingsBtn.click();
    await expect(settingsPage.accountSettingsHeader).toBeVisible({ timeout: TIMEOUT_30_SECONDS }); // generous time

    // click 'Connected Accounts' button and verify corresponding settings appear
    await settingsPage.connectedSettingsBtn.click();
    await expect(settingsPage.connectedSettingsHeader).toBeVisible({ timeout: TIMEOUT_30_SECONDS }); // generous time

    // click 'General' button and verify general settings appear once again
    await settingsPage.generalSettingsBtn.click();
    await expect(settingsPage.generalSettingsHeaderEN).toBeVisible({ timeout: TIMEOUT_30_SECONDS }); // generous time
  });
});
