import { test, expect } from '@playwright/test';
import { SettingsPage } from '../../pages/settings-page';
import { DashboardPage } from '../../pages/dashboard-page';
import { mobileSignInAndSetup } from '../../utils/utils';

import {
  PLAYWRIGHT_TAG_E2E_MOBILE_SUITE,
  PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY,
  TIMEOUT_1_SECOND,
  TIMEOUT_3_SECONDS,
  TIMEOUT_30_SECONDS,
 } from '../../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('settings - connected applications on mobile browser', {
  tag: [PLAYWRIGHT_TAG_E2E_MOBILE_SUITE, PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }, testInfo) => {
    settingsPage = new SettingsPage(page, testInfo.project.name); // i.e. 'ios-safari'
    dashboardPage = new DashboardPage(page);

    // mobile browsers don't support saving auth storage state so must sign in before each test
    // send in the playright test project name i.e. safari-ios because some mobile platforms differ
    await mobileSignInAndSetup(page, testInfo.project.name);

    // navigate to the settings page, connected apps section
    await settingsPage.gotoConnectedAppSettings();
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
  });

  test.afterEach(async ({ page }) => {
    // close the browser page when we're done so it doesn't stay as a tab on mobile browser
    await page.close();
  });

  test('verify connected applications settings on mobile browser', async ({ page }) => {
    // verify section header
    await expect(settingsPage.connectedAppsHdr).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await settingsPage.scrollIntoView(settingsPage.connectedAppsHdr);

    // one of the calendars is marked with the default badge; if there is more than one badge found this will fail
    await expect(settingsPage.defaultCalendarBadge).toBeVisible();
    await settingsPage.scrollIntoView(settingsPage.defaultCalendarBadge);

    // verify that clicking the 'add caldav' button brings up the caldav connection dialog; just close it
    await settingsPage.scrollIntoView(settingsPage.addCaldavBtn);
    await settingsPage.addCaldavBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await expect(settingsPage.addCaldavUsernameInput).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await settingsPage.scrollIntoView(settingsPage.addCaldavUsernameInput);
    await expect(settingsPage.addCaldavLocationInput).toBeVisible();
    await expect(settingsPage.addCaldavPasswordInput).toBeVisible();

    // on android mobile browser there is no close button for the add caldav dialog (issue 1250)
    // so to continue this test go back to the settings URL / refresh the page to close the add caldav dialog
    await settingsPage.gotoConnectedAppSettings();
    await page.waitForTimeout(TIMEOUT_3_SECONDS);

    // verify clicking the 'add google calendar' button brings up the google sign-in url
    await settingsPage.addGoogleBtn.click();
    await expect(settingsPage.googleSignInHdr).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
  });

  test.afterAll(async ({ browser }, testInfo) => {
    // close the browser when we're done (good practice for BrowserStack); only do this for BrowserStack,
    // because if we do this when running on a local playwright mobile viewport the tests will fail
    if (!testInfo.project.name.includes('View')) {
      await browser.close();
    }
  });
});
