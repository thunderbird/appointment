import { test, expect } from '@playwright/test';
import { SettingsPage } from '../pages/settings-page';
import { DashboardPage } from '../pages/dashboard-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  APPT_TARGET_ENV,
  TIMEOUT_1_SECOND,
  TIMEOUT_2_SECONDS,
  TIMEOUT_3_SECONDS,
  TIMEOUT_30_SECONDS,
  APPT_ACCT_SETTINGS_MAX_INVITE_CODE_COUNT,
 } from '../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('account settings - other', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    // note: we are already signed into Appointment with our default settings (via our auth-setup)
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);

    // navigate to the account settings page
    await settingsPage.gotoAccountSettingsPage();
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
      // there should be a maximum of 10 invite codes available
      const inviteCodeCount = await settingsPage.inviteCode.count();
      console.log(`found ${inviteCodeCount} invite code(s)`);
      expect(inviteCodeCount).toBeLessThanOrEqual(APPT_ACCT_SETTINGS_MAX_INVITE_CODE_COUNT);
      // read the first invite code in the list
      const firstCode = await settingsPage.inviteCode.first().textContent();
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
