import { test, expect } from '@playwright/test';
import { navigateToAppointmentAndSignIn } from '../utils/utils';
import { SettingsPage } from '../pages/settings-page';
import { PLAYWRIGHT_TAG_E2E_SUITE, APPT_MAIN_SETTINGS_PAGE } from '../const/constants';

let settingsPage: SettingsPage;

test.beforeEach(async ({ page }) => {
  // navigate to and sign into appointment
  await navigateToAppointmentAndSignIn(page);
  settingsPage = new SettingsPage(page);
});

test.describe('settings navigation', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE],
}, () => {
  test('able to navigate through the settings panels', async ({ page }) => {
    // navigate to main settings URL and verify general settings displayed by default
    await settingsPage.gotoMainSettingsPage();
    await expect(settingsPage.settingsHeaderEN).toBeVisible({ timeout: 30000 }); // generous time
    await expect(settingsPage.generalSettingsHeaderEN).toBeVisible({ timeout: 30000 }); // generous time
    await expect(settingsPage.generalSettingsBtn).toBeEnabled();
    await expect(settingsPage.calendarSettingsBtn).toBeEnabled();
    await expect(settingsPage.accountSettingsBtn).toBeEnabled();
    await expect(settingsPage.connectedSettingsBtn).toBeEnabled();

    // click 'Calendar' button and verify corresponding settings appear
    await settingsPage.calendarSettingsBtn.click();
    await expect(settingsPage.calendarSettingsHeader).toBeVisible({ timeout: 30000 }); // generous time

    // click 'Account' button and verify corresponding settings appear
    await settingsPage.accountSettingsBtn.click();
    await expect(settingsPage.accountSettingsHeader).toBeVisible({ timeout: 30000 }); // generous time

    // click 'Connected Accounts' button and verify corresponding settings appear
    await settingsPage.connectedSettingsBtn.click();
    await expect(settingsPage.connectedSettingsHeader).toBeVisible({ timeout: 30000 }); // generous time

    // click 'General' button and verify general settings appear once again
    await settingsPage.generalSettingsBtn.click();
    await expect(settingsPage.generalSettingsHeaderEN).toBeVisible({ timeout: 30000 }); // generous time
  });
});
