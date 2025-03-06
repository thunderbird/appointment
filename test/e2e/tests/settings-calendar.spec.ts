import { test, expect } from '@playwright/test';
import { navigateToAppointmentAndSignIn } from '../utils/utils';
import { SettingsPage } from '../pages/settings-page';
import { PLAYWRIGHT_TAG_E2E_SUITE } from '../const/constants';

let settingsPage: SettingsPage;

test.beforeEach(async ({ page }) => {
  // navigate to and sign into appointment
  await navigateToAppointmentAndSignIn(page);
  settingsPage = new SettingsPage(page);
});

test.describe('calendar settings', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE],
}, () => {
  test('able to...', async ({ page }) => {
    await settingsPage.gotoCalendarSettingsPage();
    // todo: when issue #908 is fixed, add a test to disconnect and re-connect google calendar
  });
});
