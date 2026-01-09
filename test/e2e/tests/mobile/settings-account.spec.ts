import { test, expect } from '@playwright/test';
import { SettingsPage } from '../../pages/settings-page';
import { DashboardPage } from '../../pages/dashboard-page';
import { AvailabilityPage } from '../../pages/availability-page';
import { BookingPage } from '../../pages/booking-page';
import { mobileSignInAndSetup } from '../../utils/utils';

import {
  PLAYWRIGHT_TAG_E2E_SUITE_MOBILE,
  PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY,
  APPT_MY_SHARE_LINK,
  APPT_DISPLAY_NAME,
  TIMEOUT_1_SECOND,
  TIMEOUT_3_SECONDS,
  TIMEOUT_30_SECONDS,
  TIMEOUT_2_SECONDS,
 } from '../../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;
let availabilityPage: AvailabilityPage;
let bookApptPage: BookingPage;

test.describe('account settings on mobile browser', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE_MOBILE, PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }, testInfo) => {
    settingsPage = new SettingsPage(page, testInfo.project.name); // i.e. 'ios-safari'
    dashboardPage = new DashboardPage(page);
    availabilityPage = new AvailabilityPage(page);
    bookApptPage = new BookingPage(page, testInfo.project.name); // i.e. 'ios-safari'

    // mobile browsers don't support saving auth storage state so must sign in before each test
    // send in the playright test project name i.e. safari-ios because some mobile platforms differ
    await mobileSignInAndSetup(page, testInfo.project.name);

    // navigate to settings page, account settings section
    await settingsPage.gotoAccountSettings();
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
  });

  test.afterEach(async ({ page }) => {
    // close the browser page when we're done so it doesn't stay as a tab on mobile browser
    await page.close();
  });

  test('verify account settings on mobile browser', async ({ page }, testInfo) => {
    // verify section header
    await expect(settingsPage.accountSettingsHeader).toBeVisible();

    // verify display name displayed is as expected
    await expect(settingsPage.displayNameInput).toBeVisible();
    expect(await settingsPage.displayNameInput.inputValue()).toBe(APPT_DISPLAY_NAME);

    // verify booking page url displayed is correct
    await settingsPage.scrollIntoView(settingsPage.bookingPageURLInput);
    expect(await settingsPage.bookingPageURLInput.inputValue()).toBe(APPT_MY_SHARE_LINK);

    // ensure we can click the copy link button; note: we can't access clipboard in firefox b/c of security
    await settingsPage.scrollIntoView(settingsPage.copyLinkBtn);
    if (!testInfo.project.name.includes('ios')) { // 'toBeEnabled' is not supported on BrowserStack for ios at least not yet
      await expect(settingsPage.copyLinkBtn).toBeEnabled();  
    }
    await settingsPage.copyLinkBtn.click();

    // just ensure the download your data button exists and is enabled as don't want to actually
    // download and leave potenial sensitive data on the test instance
    await settingsPage.scrollIntoView(settingsPage.downloadDataBtn);
    await expect(settingsPage.downloadDataBtn).toBeVisible();

    // delete all data button brings up confirmation dialog (just cancel out)
    await settingsPage.scrollIntoView(settingsPage.deleteDataBtn);
    await settingsPage.deleteDataBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await settingsPage.scrollIntoView(settingsPage.deleteDataConfirmCancelBtn);
    await settingsPage.deleteDataConfirmCancelBtn.click({ timeout: TIMEOUT_30_SECONDS });
    await page.waitForTimeout(TIMEOUT_1_SECOND);

    // clicking 'manage booking' link brings up availability page
    await settingsPage.scrollIntoView(settingsPage.manageBookingLink);
    await settingsPage.manageBookingLink.click();
    await expect(availabilityPage.setAvailabilityText).toBeVisible();
  });

  test.afterAll(async ({ browser }, testInfo) => {
    // close the browser when we're done (good practice for BrowserStack); only do this for BrowserStack,
    // because if we do this when running on a local playwright mobile viewport the tests will fail
    if (!testInfo.project.name.includes('View')) {
      await browser.close();
    }
  });
});
