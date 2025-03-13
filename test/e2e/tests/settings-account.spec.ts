import { test, expect } from '@playwright/test';
import { navigateToAppointmentAndSignIn } from '../utils/utils';
import { SettingsPage } from '../pages/settings-page';
import { DashboardPage } from '../pages/dashboard-page';
import { PLAYWRIGHT_TAG_E2E_SUITE, APPT_LOGIN_EMAIL, APPT_DISPLAY_NAME, APPT_MY_SHARE_LINK, APPT_TARGET_ENV } from '../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.beforeEach(async ({ page }) => {
  // navigate to and sign into appointment
  await navigateToAppointmentAndSignIn(page);
  settingsPage = new SettingsPage(page);
  dashboardPage = new DashboardPage(page);
});

test.describe('account settings', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE],
}, () => {
  test('verify profile details', async ({ page }) => {
    await settingsPage.gotoAccountSettingsPage();
    // verify user name, preferred email, display name, and share link are all correct
    expect(await settingsPage.getAccountProfileUsername()).toBe(APPT_LOGIN_EMAIL);
    expect(await settingsPage.getAccountProfilePreferredEmail()).toBe(APPT_LOGIN_EMAIL);
    expect(await settingsPage.getAccountProfileDisplayName()).toBe(APPT_DISPLAY_NAME);
    expect(await settingsPage.getAccountProfileMyLink()).toBe(APPT_MY_SHARE_LINK);
  });

  test('able to change display name', async ({ page }) => {
    await settingsPage.gotoAccountSettingsPage();
    // note that currently on stage the display name is not being updated after being changed
    // so this test case will fail until issue #924 is fixed

    // change the account settings user display name and save; we use expect.soft here because if the expect
    // fails we still want the test to continue so that the test will change the setting back to original
    // value (expect.soft will still mark the test case failed if the expect fails, but won't stop the test)
    const newDisplayName: string = 'Display name modified by E2E!'
    await settingsPage.setAccountProfileDisplayName(newDisplayName);
    expect.soft(await settingsPage.getAccountProfileDisplayName()).toBe(newDisplayName);

    // verify new display name is now displayed on the dashboard
    await dashboardPage.gotoToDashboardMonthView();
    expect.soft(await dashboardPage.getAvailabilityPanelHeader()).toContain(newDisplayName);

    // now change the display name setting back to what it was before, and save
    await settingsPage.gotoAccountSettingsPage();
    await settingsPage.setAccountProfileDisplayName(APPT_DISPLAY_NAME);
    expect(await settingsPage.getAccountProfileDisplayName()).toBe(APPT_DISPLAY_NAME);

    // verify new display name is now displayed on the dashboard
    await dashboardPage.gotoToDashboardMonthView();
    expect(await dashboardPage.getAvailabilityPanelHeader()).toContain(APPT_DISPLAY_NAME);
  });

  test('refresh link button', async ({ page }) => {
    await settingsPage.gotoAccountSettingsPage();
    // verify that clicking the refresh link button results in a refresh link confirm dialog
    // won't actually refresh the link as that would break the other E2E tests
    expect(settingsPage.refreshLinkBtn).toBeEnabled();
    await settingsPage.refreshLinkBtn.click();
    await settingsPage.confirmRefreshCancelBtn.click();
  });

  test('invite codes available', async ({ page }) => {
    await settingsPage.gotoAccountSettingsPage();
    await expect(settingsPage.inviteCodesHeader).toBeVisible({ timeout: 30000 }); // generous time in case a large list
    // verify invite codes are available; note on local dev environment they won't be any
    if (APPT_TARGET_ENV == 'dev') {
      await expect(settingsPage.noInviteCodesCell).toBeVisible();
    } else {
      await expect(settingsPage.noInviteCodesCell).not.toBeVisible();
      // todo check for an actual code
    }
  });
});
