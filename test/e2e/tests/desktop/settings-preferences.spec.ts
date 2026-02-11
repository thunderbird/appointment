import { test, expect } from '@playwright/test';
import { SettingsPage } from '../../pages/settings-page';
import { DashboardPage } from '../../pages/dashboard-page';
import { ensureWeAreSignedIn } from '../../utils/utils';

import {
  PLAYWRIGHT_TAG_E2E_DESKTOP_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
 } from '../../const/constants';
import { set } from 'date-fns/set';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('settings - preferences on desktop browser', {
  tag: [PLAYWRIGHT_TAG_E2E_DESKTOP_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    await ensureWeAreSignedIn(page);
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);

    // navigate to the settings page, preferences section
    await settingsPage.gotoPreferencesSettings();
  });

  test('settings options are available on desktop browser', async ({ page }) => {
    // theme
    await expect(settingsPage.themeSelect).toBeVisible();
    await expect(settingsPage.themeSelect).toBeEnabled();
    await settingsPage.themeSelect.scrollIntoViewIfNeeded();

    // language
    await expect(settingsPage.languageSelect).toBeVisible();
    await expect(settingsPage.languageSelect).toBeEnabled();

    // default timezone
    await expect(settingsPage.defaultTimeZoneSelect).toBeVisible();
    await expect(settingsPage.defaultTimeZoneSelect).toBeEnabled();

    // time format
    await expect(settingsPage.timeFormat12HrBtn).toBeVisible();
    await expect(settingsPage.timeFormat12HrBtn).toBeEnabled();
    await expect(settingsPage.timeFormat24HrBtn).toBeVisible();
    await expect(settingsPage.timeFormat24HrBtn).toBeEnabled();

    // start of week
    await expect(settingsPage.startOfWeekMonBtn).toBeVisible();
    await expect(settingsPage.startOfWeekMonBtn).toBeEnabled();
    await expect(settingsPage.startOfWeekTueBtn).toBeVisible();
    await expect(settingsPage.startOfWeekTueBtn).toBeEnabled();
    await expect(settingsPage.startOfWeekWedBtn).toBeVisible();
    await expect(settingsPage.startOfWeekWedBtn).toBeEnabled();
    await expect(settingsPage.startOfWeekThuBtn).toBeVisible();
    await expect(settingsPage.startOfWeekThuBtn).toBeEnabled();
    await expect(settingsPage.startOfWeekFriBtn).toBeVisible();
    await expect(settingsPage.startOfWeekFriBtn).toBeEnabled();
    await expect(settingsPage.startOfWeekSatBtn).toBeVisible();
    await expect(settingsPage.startOfWeekSatBtn).toBeEnabled();
    await expect(settingsPage.startOfWeekSunBtn).toBeVisible();
    await expect(settingsPage.startOfWeekSunBtn).toBeEnabled();
  });
});
