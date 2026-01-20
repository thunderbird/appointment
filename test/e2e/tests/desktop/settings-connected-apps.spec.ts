import { test, expect } from '@playwright/test';
import { SettingsPage } from '../../pages/settings-page';
import { DashboardPage } from '../../pages/dashboard-page';
import { ensureWeAreSignedIn } from '../../utils/utils';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  TIMEOUT_1_SECOND,
  TIMEOUT_30_SECONDS,
  TIMEOUT_3_SECONDS,
 } from '../../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('connected applications settings on desktop browser', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    await ensureWeAreSignedIn(page);
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);
    // navigate to the settings page, connected apps section
    await settingsPage.gotoConnectedAppSettings();
  });

  test('verify connected applications settings on desktop browser', async ({ page }) => {
    // verify section header
    await expect(settingsPage.connectedAppsHdr).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await settingsPage.connectedAppsHdr.scrollIntoViewIfNeeded();

    // one of the calendars is marked with the default badge; if there is more than one badge found this will fail
    await expect(settingsPage.defaultCalendarBadge).toBeVisible();
    await settingsPage.defaultCalendarBadge.scrollIntoViewIfNeeded();

    // verify that clicking the 'add caldav' button brings up the caldav connection dialog; just close it
    await settingsPage.addCaldavBtn.scrollIntoViewIfNeeded();
    await settingsPage.addCaldavBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await expect(settingsPage.addCaldavUsernameInput).toBeVisible();
    await expect(settingsPage.addCaldavLocationInput).toBeVisible();
    await expect(settingsPage.addCaldavPasswordInput).toBeVisible();
    await settingsPage.addCaldavCloseModalBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);

    // verify clicking the 'add google calendar' button brings up the google sign-in url
    await settingsPage.addGoogleBtn.click();
    await expect(settingsPage.googleSignInHdr).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await settingsPage.gotoConnectedAppSettings();
  });
});
