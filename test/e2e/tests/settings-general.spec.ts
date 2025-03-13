import { test, expect } from '@playwright/test';
import { navigateToAppointmentAndSignIn } from '../utils/utils';
import { SettingsPage } from '../pages/settings-page';
import { DashboardPage } from '../pages/dashboard-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  APPT_LANGUAGE_SETTING_DE,
  APPT_LANGUAGE_SETTING_EN,
  APPT_THEME_SETTING_DARK,
  APPT_THEME_SETTING_LIGHT,
  APPT_TIMEZONE_SETTING_TORONTO,
  APPT_TIMEZONE_SETTING_HALIFAX,
 } from '../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.beforeEach(async ({ page }) => {
  // navigate to and sign into appointment
  await navigateToAppointmentAndSignIn(page);
  settingsPage = new SettingsPage(page);
  dashboardPage = new DashboardPage(page);

  // navigate to the general settings page
  await settingsPage.gotoGeneralSettingsPage();
});

test.describe('general settings', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE],
}, () => {
  test('able to change language', async ({ page }) => {
    // change language setting to DE and verify; we use expect.soft here because if the expect fails
    // we still want the test to continue so that the test will change the setting back to original value
    // (expect.soft will still mark the test case failed if the expect fails, but won't stop the test)
    await settingsPage.changeLanguageSetting(APPT_LANGUAGE_SETTING_DE);
    await expect.soft(settingsPage.settingsHeaderDE).toBeVisible({ timeout: 15000 });
    await expect.soft(settingsPage.generalSettingsHeaderDE).toBeVisible();

    // change language settings back to EN and verify
    await settingsPage.changeLanguageSetting(APPT_LANGUAGE_SETTING_EN);
    await expect(settingsPage.settingsHeaderEN).toBeVisible({ timeout: 15000 });
    await expect(settingsPage.generalSettingsHeaderEN).toBeVisible();
  });

  test('able to change theme', async ({ page }) => {
    // change theme setting to dark mode and verify
    await settingsPage.changeThemeSetting(APPT_THEME_SETTING_DARK);
    expect.soft(await settingsPage.isDarkModeEnabled(page)).toBeTruthy();

    // change theme setting back to light mode and verify
    await settingsPage.changeThemeSetting(APPT_THEME_SETTING_LIGHT);
    expect(await settingsPage.isDarkModeEnabled(page)).toBeFalsy();
  });

  test('able to change time format', async ({ page }) => {
    // change time format setting to 24-hour format and verify on dashboard calendar
    await settingsPage.set24hrFormat();
    await dashboardPage.gotoToDashboardMonthView();
    await expect.soft(dashboardPage.calendarEvent24hrFormat).toBeVisible({ timeout: 30000 });
    await settingsPage.gotoGeneralSettingsPage();

    // change time format setting back to 12-hour format and verify on dashboard calendar
    await settingsPage.set12hrFormat();
    await dashboardPage.gotoToDashboardMonthView();
    await expect(dashboardPage.calendarEvent24hrFormat).not.toBeVisible({ timeout: 30000 });
  });

  test('able to change timezone', async ({ page }) => {
    // change time zone setting and verify on dashboard calendar
    await settingsPage.changeTimezoneSetting(APPT_TIMEZONE_SETTING_HALIFAX);
    await dashboardPage.gotoToDashboardMonthView();
    await expect.soft(dashboardPage.timezoneDisplayTextHalifax).toBeVisible({ timeout: 30000 });

    // change time format setting back and verify on dashboard calendar
    await settingsPage.gotoGeneralSettingsPage();
    await settingsPage.changeTimezoneSetting(APPT_TIMEZONE_SETTING_TORONTO);
    await dashboardPage.gotoToDashboardMonthView();
    await expect(dashboardPage.timezoneDisplayTextToronto).toBeVisible({ timeout: 30000 });
  });
});
