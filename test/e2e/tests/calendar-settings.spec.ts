import { test, expect } from '@playwright/test';
import { SettingsPage } from '../pages/settings-page';
import { DashboardPage } from '../pages/dashboard-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  TIMEOUT_2_SECONDS,
  TIMEOUT_3_SECONDS,
  TIMEOUT_30_SECONDS,
 } from '../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('calendar settings', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    // note: we are already signed into Appointment with our default settings (via our auth-setup)
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);

    // navigate to the calendar settings page
    await settingsPage.gotoCalendarSettingsPage();
  });

  test('able to sync calendars', async ({ page }) => {
    // click the 'sync calendars button'
    await expect(settingsPage.syncCalendarsBtn).toBeEnabled();
    await settingsPage.syncCalendarsBtn.click();
    await expect(settingsPage.syncCalendarsBtn).toBeDisabled();
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
  });

  test('able to edit calendar', async ({ page }) => {
    // verify calendar is already connected
    await expect(settingsPage.connectedCalendarsHeader).toBeVisible({ timeout: TIMEOUT_30_SECONDS }); // generous time
    await expect(settingsPage.editCalendarBtn).toBeEnabled();
    await expect(settingsPage.connectedCalendarTitle).toBeVisible();

    // edit the connected calendar and cancel out
    await settingsPage.editCalendarBtn.click();
    await page.waitForTimeout(TIMEOUT_2_SECONDS);
    await expect(settingsPage.editCalendarTitleInput).toBeEnabled();
    await expect(settingsPage.editCalendarColorInput).toBeEnabled();
    await settingsPage.editCalendarCancelBtn.click();
  });

  test('add google calendar button', async ({ page }) => {
    // just verify the 'connect google calendar' button becomes available then cancel out
    await expect(settingsPage.addGoogleCalendarBtn).toBeEnabled();
    await settingsPage.addGoogleCalendarBtn.click();
    await expect(settingsPage.connectGoogleCalendarBtn).toBeEnabled();
    await settingsPage.editCalendarCancelBtn.click();
  });

  test('add caldav calendar button', async ({ page }) => {
    // just verify the discover caldav calendar fields appear then cancel out
    await expect(settingsPage.addCaldavCalendarBtn).toBeEnabled({ timeout: TIMEOUT_30_SECONDS });
    await settingsPage.addCaldavCalendarBtn.click();
    await page.waitForTimeout(TIMEOUT_2_SECONDS);
    await expect(settingsPage.addCaldavUrlInput).toBeEnabled({ timeout: TIMEOUT_30_SECONDS });
    await expect(settingsPage.addCaldavUserInput).toBeEnabled();
    await expect(settingsPage.addCaldavPasswordInput).toBeEnabled();
    await settingsPage.editCalendarCancelBtn.click();
  });
});
