import { test, expect } from '@playwright/test';
import { navigateToAppointmentAndSignIn, getUserSettingsFromLocalStore, setDefaultUserSettingsLocalStore } from '../utils/utils';
import { SettingsPage } from '../pages/settings-page';
import { DashboardPage } from '../pages/dashboard-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  PLAYWRIGHT_TAG_PROD_NIGHTLY_MOBILE,
  APPT_LANGUAGE_SETTING_DE,
  APPT_LANGUAGE_SETTING_EN,
  APPT_THEME_SETTING_DARK,
  APPT_THEME_SETTING_LIGHT,
  APPT_TIMEZONE_SETTING_TORONTO,
  APPT_TIMEZONE_SETTING_HALIFAX,
  TIMEOUT_1_SECOND,
  TIMEOUT_2_SECONDS,
  TIMEOUT_3_SECONDS,
  TIMEOUT_30_SECONDS,
  APPT_BROWSER_STORE_LANGUAGE_EN,
  APPT_BROWSER_STORE_LANGUAGE_DE,
  APPT_BROWSER_STORE_THEME_LIGHT,
  APPT_BROWSER_STORE_THEME_DARK,
  APPT_BROWSER_STORE_12HR_TIME,
  APPT_BROWSER_STORE_24HR_TIME,
  APPT_BROWSER_STORE_START_WEEK_MON,
  APPT_BROWSER_STORE_START_WEEK_SUN,
  APPT_START_OF_WEEK_MON,
  APPT_START_OF_WEEK_SUN,
  APPT_START_OF_WEEK_DASHBOARD_MON,
  APPT_START_OF_WEEK_DASHBOARD_SUN,
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

test.describe('general settings', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY, PLAYWRIGHT_TAG_PROD_NIGHTLY_MOBILE],
}, () => {
  test.beforeEach(async ({ page }) => {
    // navigate to and sign into appointment
    await navigateToAppointmentAndSignIn(page);
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);

    // navigate to the general settings page
    await settingsPage.gotoGeneralSettingsPage();

    // ensure our settings are set to what the tests expect as default (in case a
    // previous test run failed and left the settings in an incorrect state)
    await setDefaultUserSettingsLocalStore(page);
    await page.reload();
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
  });

  test('able to change language', async ({ page }) => {
    // change language setting to DE and verify; we use expect.soft here because if the expect fails
    // we still want the test to continue so that the test will change the setting back to original value
    // (expect.soft will still mark the test case failed if the expect fails, but won't stop the test)
    await settingsPage.changeLanguageSetting(APPT_LANGUAGE_SETTING_DE);
    await expect.soft(settingsPage.settingsHeaderDE).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await expect.soft(settingsPage.generalSettingsHeaderDE).toBeVisible();

    // verify setting saved in browser local storage
    let localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['language']).toBe(APPT_BROWSER_STORE_LANGUAGE_DE);

    // change language settings back to EN and verify
    await settingsPage.changeLanguageSetting(APPT_LANGUAGE_SETTING_EN);
    await expect(settingsPage.settingsHeaderEN).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await expect(settingsPage.generalSettingsHeaderEN).toBeVisible();

    // verify setting saved in browser local storage
    localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['language']).toBe(APPT_BROWSER_STORE_LANGUAGE_EN);
  });

  test('able to change theme', async ({ page }) => {
    // change theme setting to dark mode and verify
    await settingsPage.changeThemeSetting(APPT_THEME_SETTING_DARK);
    expect.soft(await settingsPage.isDarkModeEnabled(page)).toBeTruthy();

    // verify setting saved in browser local storage
    let localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['colourScheme']).toBe(APPT_BROWSER_STORE_THEME_DARK);

    // change theme setting back to light mode and verify
    await settingsPage.changeThemeSetting(APPT_THEME_SETTING_LIGHT);
    expect(await settingsPage.isDarkModeEnabled(page)).toBeFalsy();
  
    // verify setting saved in browser local storage
    localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['colourScheme']).toBe(APPT_BROWSER_STORE_THEME_LIGHT);
  });

  test('able to change time format', async ({ page }) => {
    // change time format setting to 24-hour format and verify
    await settingsPage.set24hrFormat();

    // verify setting saved in browser local storage
    await settingsPage.gotoGeneralSettingsPage();
    let localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['timeFormat']).toBe(APPT_BROWSER_STORE_24HR_TIME);

    // change time format setting back to 12-hour format
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
    await settingsPage.gotoGeneralSettingsPage();
    await settingsPage.set12hrFormat();

    // verify setting saved in browser local storage
    await settingsPage.gotoGeneralSettingsPage();
    localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['timeFormat']).toBe(APPT_BROWSER_STORE_12HR_TIME); 
  });

  test('able to change timezone', async ({ page }) => {
    // change time zone setting
    await settingsPage.timeZoneSelect.scrollIntoViewIfNeeded();
    await page.waitForTimeout(TIMEOUT_2_SECONDS);
    await settingsPage.changeTimezoneSetting(APPT_TIMEZONE_SETTING_HALIFAX);

    // verify setting saved in browser local storage
    let localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['timezone']).toBe(APPT_TIMEZONE_SETTING_HALIFAX);

    // verify new time zone shows on dashboard
    await dashboardPage.gotoToDashboardMonthView();
    await dashboardPage.timezoneLabel.scrollIntoViewIfNeeded();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await expect.soft(dashboardPage.timezoneDisplayTextHalifax).toBeVisible({ timeout: TIMEOUT_30_SECONDS });

    // change time format setting back
    await settingsPage.gotoGeneralSettingsPage();
    await settingsPage.timeZoneSelect.scrollIntoViewIfNeeded();
    await page.waitForTimeout(TIMEOUT_2_SECONDS);
    await settingsPage.changeTimezoneSetting(APPT_TIMEZONE_SETTING_TORONTO);

    // verify setting saved in browser local storage
    localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['timezone']).toBe(APPT_TIMEZONE_SETTING_TORONTO);

    // verify timezone changed on dashboard
    await dashboardPage.gotoToDashboardMonthView();
    await dashboardPage.timezoneLabel.scrollIntoViewIfNeeded();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await expect(dashboardPage.timezoneDisplayTextToronto).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
  });

  test('able to change start of week', async ({ page }) => {
    // change start of week to Monday and verify
    await settingsPage.changeStartOfWeekSetting(APPT_START_OF_WEEK_MON);

    // verify setting saved in browser local storage
    await settingsPage.gotoGeneralSettingsPage();
    let localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['startOfWeek']).toBe(APPT_BROWSER_STORE_START_WEEK_MON);

    // verify on dashboard
    await dashboardPage.gotoToDashboardMonthView();
    var firstDayOfWeekText = await dashboardPage.firstDayOfWeekMonthView.innerText();
    expect(firstDayOfWeekText).toEqual(APPT_START_OF_WEEK_DASHBOARD_MON);

    // change start of week back to Sunday and verify
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
    await settingsPage.gotoGeneralSettingsPage();
    await settingsPage.changeStartOfWeekSetting(APPT_START_OF_WEEK_SUN);

    // verify setting saved in browser local storage
    await settingsPage.gotoGeneralSettingsPage();
    localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['startOfWeek']).toBe(APPT_BROWSER_STORE_START_WEEK_SUN);

    // verify on dashboard
    await dashboardPage.gotoToDashboardMonthView();
    firstDayOfWeekText = await dashboardPage.firstDayOfWeekMonthView.innerText();
    expect(firstDayOfWeekText).toEqual(APPT_START_OF_WEEK_DASHBOARD_SUN);
  });
});
