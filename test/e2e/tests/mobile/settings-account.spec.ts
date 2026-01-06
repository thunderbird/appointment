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
    bookApptPage = new BookingPage(page);

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

    // click copy link button and verify copied link is correct
    // note: we can't access clipboard in firefox b/c of security so instead we will:
    //  - get the contents of the booking page URL input field (correct link)
    //  - click the copy link button
    //  - clear the booking page URL input field so it is empty
    //  - focus on the booking page URL input field
    //  - do a keyboard paste into the field
    //  - retrieve the new contents of the booking page url after the paste into that field
    //  - verify the input field now has the correct link url
    const correctBookingUrl = await settingsPage.bookingPageURLInput.inputValue();
    await settingsPage.copyLinkBtn.click();
    await settingsPage.bookingPageURLInput.clear();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await settingsPage.bookingPageURLInput.focus();
    // paste using keyboard, different command for ios
    if (testInfo.project.name.includes('ios')) {
      await page.keyboard.press('Meta+V');
    } else {
      await page.keyboard.press('ControlOrMeta+V');
    }
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    const afterPasteBookingUrl = await settingsPage.bookingPageURLInput.inputValue();
    expect(afterPasteBookingUrl).toEqual(correctBookingUrl);

    // just ensure the download your data button exists and is enabled as don't want to actually
    // download and leave potenial sensitive data on the test instance
    await settingsPage.scrollIntoView(settingsPage.downloadDataBtn);
    await expect(settingsPage.downloadDataBtn).toBeVisible();

    // cancel service button brings up confirmation dialog (just cancel out)
    await settingsPage.scrollIntoView(settingsPage.cancelServiceBtn);
    await settingsPage.cancelServiceBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await settingsPage.scrollIntoView(settingsPage.cancelServiceConfirmCancelBtn);
    await settingsPage.cancelServiceConfirmCancelBtn.click({ timeout: TIMEOUT_30_SECONDS });
    await page.waitForTimeout(TIMEOUT_1_SECOND);

    // clicking 'booking page settings' button brings up availability section
    await settingsPage.scrollIntoView(settingsPage.bookingPageSettingsBtn);
    await settingsPage.bookingPageSettingsBtn.click();
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
