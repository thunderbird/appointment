import { test, expect } from '@playwright/test';
import { navigateToAppointmentAndSignIn, setDefaultUserSettingsLocalStore } from '../utils/utils';
import { SettingsPage } from '../pages/settings-page';
import { DashboardPage } from '../pages/dashboard-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  APPT_LOGIN_EMAIL,
  APPT_DISPLAY_NAME,
  APPT_MY_SHARE_LINK,
  APPT_TARGET_ENV,
  TIMEOUT_1_SECOND,
  TIMEOUT_2_SECONDS,
  TIMEOUT_3_SECONDS,
  TIMEOUT_30_SECONDS,
 } from '../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('account settings', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    // navigate to and sign into appointment
    await navigateToAppointmentAndSignIn(page);
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);

    // ensure our settings are set to what the tests expect as default (in case a
    // previous test run failed and left the settings in an incorrect state)
    await setDefaultUserSettingsLocalStore(page);

    // navigate to the account settings page
    await settingsPage.gotoAccountSettingsPage();
  });

  test('verify profile details', async ({ page }) => {
    // verify user name, preferred email, display name
    expect(await settingsPage.getAccountProfileUsername()).toBe(APPT_LOGIN_EMAIL);
    expect(await settingsPage.getAccountProfilePreferredEmail()).toBe(APPT_LOGIN_EMAIL);
    expect(await settingsPage.getAccountProfileDisplayName()).toBe(APPT_DISPLAY_NAME);

    // verify the displayed share link; there are two parts to the share link, a label that contains
    // the root URL (host and username), and an input field that contains an optional slug; note that
    // the label may not display the entire root URL as it is limited in size. Our test/e2e/.env
    // contains the full share link in APPT_MY_SHARE_LINK. Just verify that the first N chars of the
    // URL displayed in the share link label, and the optional input field value / slug are both
    // inside APPT_MY_SHARE_LINK.
    let shareLinkLabel = await settingsPage.profileMyLinkOptionalInput.innerText();
    expect(APPT_MY_SHARE_LINK).toContain(shareLinkLabel.substring(0, 15));
    let shareLinkOptionalSlug: string = await settingsPage.profileMyLinkOptionalInput.inputValue();
    if (shareLinkOptionalSlug.length) {
      expect(APPT_MY_SHARE_LINK).toContain(shareLinkOptionalSlug);
    }
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
    const downloadPromise = page.waitForEvent('download', { timeout: TIMEOUT_30_SECONDS });
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
    await settingsPage.deleteAcctBtn.scrollIntoViewIfNeeded();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await expect(settingsPage.deleteAcctBtn).toBeEnabled();
    await settingsPage.deleteAcctBtn.click();
    await page.waitForTimeout(TIMEOUT_2_SECONDS);
    await settingsPage.confirmDeleteAcctBtn.click();
  });
});

test.describe('connected accounts settings', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
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
