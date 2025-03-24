import { test, expect } from '@playwright/test';
import { navigateToAppointmentAndSignIn, getUserSettingsFromLocalStore } from '../utils/utils';
import { SettingsPage } from '../pages/settings-page';
import { DashboardPage } from '../pages/dashboard-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  APPT_LOGIN_EMAIL,
  APPT_DISPLAY_NAME,
  APPT_MY_SHARE_LINK,
  APPT_TARGET_ENV,
  APPT_LANGUAGE_SETTING_DE,
  APPT_LANGUAGE_SETTING_EN,
  APPT_THEME_SETTING_DARK,
  APPT_THEME_SETTING_LIGHT,
  APPT_TIMEZONE_SETTING_TORONTO,
  APPT_TIMEZONE_SETTING_HALIFAX,
  TIMEOUT_3_SECONDS,
  TIMEOUT_30_SECONDS,
  APPT_BROWSER_STORE_LANGUAGE_EN,
  APPT_BROWSER_STORE_LANGUAGE_DE,
  APPT_BROWSER_STORE_THEME_LIGHT,
  APPT_BROWSER_STORE_THEME_DARK,
  APPT_BROWSER_STORE_12HR_TIME,
  APPT_BROWSER_STORE_24HR_TIME,
 } from '../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('settings navigation', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE],
}, () => {
  test.beforeEach(async ({ page }) => {
    // navigate to and sign into appointment
    await navigateToAppointmentAndSignIn(page);
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);
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
  tag: [PLAYWRIGHT_TAG_E2E_SUITE],
}, () => {
  test.beforeEach(async ({ page }) => {
    // navigate to and sign into appointment
    await navigateToAppointmentAndSignIn(page);
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);
    // navigate to the general settings page
    await settingsPage.gotoGeneralSettingsPage();
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
    // change time format setting to 24-hour format and verify on dashboard calendar
    await settingsPage.set24hrFormat();
    await dashboardPage.gotoToDashboardMonthView();
    await expect.soft(dashboardPage.calendarEvent24hrFormat).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await settingsPage.gotoGeneralSettingsPage();

    // verify setting saved in browser local storage
    let localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['timeFormat']).toBe(APPT_BROWSER_STORE_24HR_TIME);

    // change time format setting back to 12-hour format and verify on dashboard calendar
    await settingsPage.set12hrFormat();
    await dashboardPage.gotoToDashboardMonthView();
    await expect(dashboardPage.calendarEvent24hrFormat).not.toBeVisible({ timeout: TIMEOUT_30_SECONDS });

    // verify setting saved in browser local storage
    localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['timeFormat']).toBe(APPT_BROWSER_STORE_12HR_TIME); 
  });

  test('able to change timezone', async ({ page }) => {
    // change time zone setting and verify on dashboard calendar
    await settingsPage.changeTimezoneSetting(APPT_TIMEZONE_SETTING_HALIFAX);
    await dashboardPage.gotoToDashboardMonthView();
    await expect.soft(dashboardPage.timezoneDisplayTextHalifax).toBeVisible({ timeout: TIMEOUT_30_SECONDS });

    // verify setting saved in browser local storage
    let localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['timezone']).toBe(APPT_TIMEZONE_SETTING_HALIFAX);

    // change time format setting back and verify on dashboard calendar
    await settingsPage.gotoGeneralSettingsPage();
    await settingsPage.changeTimezoneSetting(APPT_TIMEZONE_SETTING_TORONTO);
    await dashboardPage.gotoToDashboardMonthView();
    await expect(dashboardPage.timezoneDisplayTextToronto).toBeVisible({ timeout: TIMEOUT_30_SECONDS });

    // verify setting saved in browser local storage
    localStore = await getUserSettingsFromLocalStore(page);
    expect(localStore['timezone']).toBe(APPT_TIMEZONE_SETTING_TORONTO);
  });
});

test.describe('calendar settings', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE],
}, () => {
  test.beforeEach(async ({ page }) => {
    // navigate to and sign into appointment
    await navigateToAppointmentAndSignIn(page);
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

    // edit the connected calendar and click save button (without making changes)
    await settingsPage.editCalendarBtn.click();
    await expect(settingsPage.editCalendarTitleInput).toBeEnabled();
    await expect(settingsPage.editCalendarColorInput).toBeEnabled();
    await settingsPage.editCalendarSaveBtn.click();
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
    await expect(settingsPage.addCaldavCalendarBtn).toBeEnabled();
    await settingsPage.addCaldavCalendarBtn.click();
    await expect(settingsPage.addCaldavUrlInput).toBeEnabled();
    await expect(settingsPage.addCaldavUserInput).toBeEnabled();
    await expect(settingsPage.addCaldavPasswordInput).toBeEnabled();
    await settingsPage.editCalendarCancelBtn.click();
  });
});

test.describe('account settings', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE],
}, () => {
  test.beforeEach(async ({ page }) => {
    // navigate to and sign into appointment
    await navigateToAppointmentAndSignIn(page);
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);
    // navigate to the account settings page
    await settingsPage.gotoAccountSettingsPage();
  });

  test('verify profile details', async ({ page }) => {
    // verify user name, preferred email, display name, and share link are all correct
    expect(await settingsPage.getAccountProfileUsername()).toBe(APPT_LOGIN_EMAIL);
    expect(await settingsPage.getAccountProfilePreferredEmail()).toBe(APPT_LOGIN_EMAIL);
    expect(await settingsPage.getAccountProfileDisplayName()).toBe(APPT_DISPLAY_NAME);
    expect(await settingsPage.getAccountProfileMyLink()).toBe(APPT_MY_SHARE_LINK);
  });

  test('able to change display name', async ({ page }) => {
    // change the account settings user display name and save; we use expect.soft here because if the expect
    // fails we still want the test to continue so that the test will change the setting back to original
    // value (expect.soft will still mark the test case failed if the expect fails, but won't stop the test)
    const newDisplayName: string = 'Display name modified by E2E!'
    await settingsPage.setAccountProfileDisplayName(newDisplayName);
    expect.soft(await settingsPage.getAccountProfileDisplayName()).toBe(newDisplayName);

    // verify new display name is now displayed on the dashboard
    await dashboardPage.gotoToDashboardMonthView();
    // note that currently on stage the display name is not being updated after being changed
    // so this test case will fail until issue #924 is fixed (uncomment line below when fixed)
    // expect.soft(await dashboardPage.getAvailabilityPanelHeader()).toContain(newDisplayName);

    // now change the display name setting back to what it was before, and save
    await settingsPage.gotoAccountSettingsPage();
    await settingsPage.setAccountProfileDisplayName(APPT_DISPLAY_NAME);
    expect(await settingsPage.getAccountProfileDisplayName()).toBe(APPT_DISPLAY_NAME);

    // verify new display name is now displayed on the dashboard
    await dashboardPage.gotoToDashboardMonthView();
    expect(await dashboardPage.getAvailabilityPanelHeader()).toContain(APPT_DISPLAY_NAME);
  });

  test('refresh link button', async ({ page }) => {
    // verify that clicking the refresh link button results in a refresh link confirm dialog
    // won't actually refresh the link as that would break the other E2E tests
    await expect(settingsPage.refreshLinkBtn).toBeEnabled();
    await settingsPage.refreshLinkBtn.click();
    await settingsPage.confirmRefreshCancelBtn.click();
  });

  test('invite codes available', async ({ page }) => {
    await expect(settingsPage.inviteCodesHeader).toBeVisible({ timeout: TIMEOUT_30_SECONDS }); // generous time in case a large list
    // verify invite codes are available; note on local dev environment they won't be any; we need a pause here because
    // sometimes even when invite codes header is visible, loading the list of actual invite codes takes a few seconds
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
    if (APPT_TARGET_ENV == 'dev') {
      await expect(settingsPage.noInviteCodesCell).toBeVisible();
    } else {
      await expect(settingsPage.noInviteCodesCell).not.toBeVisible();
      // read the first invite code in the list
      const firstCode = await settingsPage.firstInviteCode.textContent();
      expect(firstCode).toHaveLength(36); // uuid is 36 char str including hyphens
    }
  });

  test('able to download account data', async ({ page }) => {
    // setup listener for browser download event
    const downloadPromise = page.waitForEvent('download');
    // click the account settings => download your data button and confirm
    await settingsPage.downloadAccountData();
    // now verify the browser download event was triggered and downloaded without error
    const download = await downloadPromise;
    const downloadErr = await download.failure(); // waits for download to finish and checks for error
    expect(downloadErr).toBeFalsy();
  });

  test('delete account button', async ({ page }) => {
    // verify that clicking the delete account button results in a delete account confirm dialog
    // we won't actually delete the account :) as that would break the other E2E tests
    await expect(settingsPage.deleteAcctBtn).toBeEnabled();
    await settingsPage.deleteAcctBtn.click();
    await settingsPage.confirmDeleteAcctBtn.click();
  });
});

test.describe('connected accounts settings', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE],
}, () => {
  test.beforeEach(async ({ page }) => {
    // navigate to and sign into appointment
    await navigateToAppointmentAndSignIn(page);
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);
    // navigate to the connected accounts settings page
    await settingsPage.gotoConnectedAccountsSettingsPage();
  });

  test('edit profile button', async ({ page }) => {
    // verify that clicking the `edit profile` button redirects to the Mozilla Account profile page
    // note that on dev env this relies on having VITE_FXA_EDIT_PROFILE= set to point to stage FxA
    await settingsPage.editProfileBtn.click();
    // skip this on dev env because stage FxA use may or may not be setup to use with local dev
    if (APPT_TARGET_ENV !== 'dev') {
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
