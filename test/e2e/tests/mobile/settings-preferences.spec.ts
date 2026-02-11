import { test, expect } from '@playwright/test';
import { SettingsPage } from '../../pages/settings-page';
import { DashboardPage } from '../../pages/dashboard-page';
import { mobileSignInAndSetup } from '../../utils/utils';

import {
  PLAYWRIGHT_TAG_E2E_MOBILE_SUITE,
  PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY,
 } from '../../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('settings - preferences on mobile browser', {
  tag: [PLAYWRIGHT_TAG_E2E_MOBILE_SUITE, PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }, testInfo) => {
    settingsPage = new SettingsPage(page, testInfo.project.name); // i.e. 'ios-safari'
    dashboardPage = new DashboardPage(page);

    // mobile browsers don't support saving auth storage state so must sign in before each test
    // send in the playright test project name i.e. safari-ios because some mobile platforms differ
    await mobileSignInAndSetup(page, testInfo.project.name);

    // navigate to the settings page, preferences section
    await settingsPage.gotoPreferencesSettings();
  });

  test('settings options are available on mobile browser', async ({ page }) => {
    // theme
    await expect(settingsPage.themeSelect).toBeVisible();
    expect (await settingsPage.themeSelect.isEnabled()).toBeTruthy();
    await settingsPage.scrollIntoView(settingsPage.themeSelect);

    // language
    await expect(settingsPage.languageSelect).toBeVisible();
    expect (await settingsPage.languageSelect.isEnabled()).toBeTruthy();

    // default timezone
    await expect(settingsPage.defaultTimeZoneSelect).toBeVisible();
    expect (await settingsPage.defaultTimeZoneSelect.isEnabled()).toBeTruthy();

    // time format
    await expect(settingsPage.timeFormat12HrBtn).toBeVisible();
    expect (await settingsPage.timeFormat12HrBtn.isEnabled()).toBeTruthy();
    await expect(settingsPage.timeFormat24HrBtn).toBeVisible();
    expect (await settingsPage.timeFormat24HrBtn.isEnabled()).toBeTruthy();

    // start of week
    await expect(settingsPage.startOfWeekMonBtn).toBeVisible();
    expect (await settingsPage.startOfWeekMonBtn.isEnabled()).toBeTruthy();
    await expect(settingsPage.startOfWeekTueBtn).toBeVisible();
    expect (await settingsPage.startOfWeekTueBtn.isEnabled()).toBeTruthy();
    await expect(settingsPage.startOfWeekWedBtn).toBeVisible();
    expect (await settingsPage.startOfWeekWedBtn.isEnabled()).toBeTruthy();
    await expect(settingsPage.startOfWeekThuBtn).toBeVisible();
    expect (await settingsPage.startOfWeekThuBtn.isEnabled()).toBeTruthy();
    await expect(settingsPage.startOfWeekFriBtn).toBeVisible();
    expect (await settingsPage.startOfWeekFriBtn.isEnabled()).toBeTruthy();
    await expect(settingsPage.startOfWeekSatBtn).toBeVisible();
    expect (await settingsPage.startOfWeekSatBtn.isEnabled()).toBeTruthy();
    await expect(settingsPage.startOfWeekSunBtn).toBeVisible();
    expect (await settingsPage.startOfWeekSunBtn.isEnabled()).toBeTruthy();
  });
  
  test.afterAll(async ({ browser }, testInfo) => {
    // close the browser when we're done (good practice for BrowserStack); only do this for BrowserStack,
    // because if we do this when running on a local playwright mobile viewport the tests will fail
    if (!testInfo.project.name.includes('View')) {
      await browser.close();
    }
  });
});
