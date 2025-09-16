import { test, expect } from '@playwright/test';
import { SettingsPage } from '../../pages/settings-page';
import { DashboardPage } from '../../pages/dashboard-page';
import { mobileSignInAndSetup } from '../../utils/utils';

import {
  PLAYWRIGHT_TAG_E2E_SUITE_MOBILE,
  PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY,
  TIMEOUT_1_SECOND,
  TIMEOUT_3_SECONDS,
  TIMEOUT_30_SECONDS,
 } from '../../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('settings - connected applications on mobile browser', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE_MOBILE, PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);

    // mobile browsers don't support saving auth storage state so must sign in before each test
    await mobileSignInAndSetup(page);

    // navigate to the settings page, connected apps section
    await settingsPage.gotoConnectedAppSettings();
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
  });

  test('verify connected applications settings on mobile browser', async ({ page }) => {
    // verify section header
    await expect(settingsPage.connectedAppsHdr).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await settingsPage.connectedAppsHdr.scrollIntoViewIfNeeded();

    // verify default calendar checkbox is on (test expects google cal already connected); then turn it
    // off but do NOT save - just revert changes and verify checkbox is back on again after the revert changes
    await settingsPage.defaultCalendarConnectedCbox.scrollIntoViewIfNeeded();
    await settingsPage.defaultCalendarConnectedCbox.uncheck({ timeout: TIMEOUT_30_SECONDS });
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await settingsPage.revertBtn.scrollIntoViewIfNeeded();
    await settingsPage.revertBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    expect(await settingsPage.defaultCalendarConnectedCbox.isChecked()).toBeTruthy();

    // verify that clicking the 'add caldav' button brings up the caldav connection dialog; just close it
    await settingsPage.addCaldavBtn.scrollIntoViewIfNeeded();
    await settingsPage.addCaldavBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await expect(settingsPage.addCaldavUsernameInput).toBeEditable({ timeout: TIMEOUT_30_SECONDS });
    await settingsPage.addCaldavUsernameInput.scrollIntoViewIfNeeded();
    await expect(settingsPage.addCaldavLocationInput).toBeEditable();
    await expect(settingsPage.addCaldavPasswordInput).toBeEditable();

    // on android mobile browser there is no close button for the add caldav dialog (issue 1250)
    // so to continue this test go back to the settings URL / refresh the page to close the add caldav dialog
    await settingsPage.gotoConnectedAppSettings();
    await page.waitForTimeout(TIMEOUT_3_SECONDS);

    // verify clicking the 'add google calendar' button brings up the google sign-in url
    await settingsPage.addGoogleBtn.click();
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
    // will go to moz sso auth or google auth depending on local/env setup
    expect(page.url().includes('auth.mozilla') || page.url().includes('accounts.google')).toBeTruthy();
    await settingsPage.gotoConnectedAppSettings();
  });
});
