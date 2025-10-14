import { test, expect } from '@playwright/test';
import { SettingsPage } from '../../pages/settings-page';
import { DashboardPage } from '../../pages/dashboard-page';
import { AvailabilityPage } from '../../pages/availability-page';
import { BookingPage } from '../../pages/booking-page';
import { mobileSignInAndSetup, getUserDisplayNameFromLocalStore } from '../../utils/utils';

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
  test.beforeEach(async ({ page }) => {
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);
    availabilityPage = new AvailabilityPage(page);
    bookApptPage = new BookingPage(page);

    // mobile browsers don't support saving auth storage state so must sign in before each test
    await mobileSignInAndSetup(page);

    // navigate to settings page, account settings section
    await settingsPage.gotoAccountSettings();
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
  });

  test('verify account settings on mobile browser', async ({ page }) => {
    // verify section header
    await expect(settingsPage.accountSettingsHeader).toBeVisible();

    // verify display name displayed is as expected
    await expect(settingsPage.displayNameInput).toBeVisible();
    expect(await settingsPage.displayNameInput.inputValue()).toBe(APPT_DISPLAY_NAME);

    // verify booking page url displayed is correct
    await settingsPage.bookingPageURLInput.scrollIntoViewIfNeeded();
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
    await page.keyboard.press('ControlOrMeta+V');
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    const afterPasteBookingUrl = await settingsPage.bookingPageURLInput.inputValue();
    expect(afterPasteBookingUrl).toEqual(correctBookingUrl);

    // just ensure the download your data button exists and is enabled as don't want to actually
    // download and leave potenial sensitive data on the test instance
    await settingsPage.downloadDataBtn.scrollIntoViewIfNeeded();
    await expect(settingsPage.downloadDataBtn).toBeVisible();
    await expect(settingsPage.downloadDataBtn).toBeEnabled();

    // cancel service button brings up confirmation dialog (just cancel out)
    await settingsPage.cancelServiceBtn.scrollIntoViewIfNeeded();
    await settingsPage.cancelServiceBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await settingsPage.cancelServiceConfirmCancelBtn.scrollIntoViewIfNeeded();
    await settingsPage.cancelServiceConfirmCancelBtn.click({ timeout: TIMEOUT_30_SECONDS });
    await page.waitForTimeout(TIMEOUT_1_SECOND);

    // clicking 'booking page settings' button brings up availability page
    await settingsPage.bookingPageSettingsBtn.scrollIntoViewIfNeeded();
    await settingsPage.bookingPageSettingsBtn.click();
    await page.waitForURL('**/availability');
    await expect(availabilityPage.setAvailabilityText).toBeVisible();
  });

  test('able to change display name on mobile browser', async ({ page }) => {
    // change display name and verify
    const newDisplayName = `Name modified by E2E test at ${new Date().toDateString()}`;
    await settingsPage.changeDisplaName(newDisplayName);

    // verify setting saved in browser local storage
    expect.soft(await getUserDisplayNameFromLocalStore(page)).toBe(newDisplayName);

    // go to share link/book appointment page and verify display name was changed;
    // expect soft so that display name will be changed back even if the test fails
    await page.goto(APPT_MY_SHARE_LINK);
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
    await expect.soft(bookApptPage.invitingText).toContainText(newDisplayName);

    // change display name back
    await settingsPage.gotoAccountSettings();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await settingsPage.changeDisplaName(APPT_DISPLAY_NAME);

    // verify setting saved in browser local storage
    expect(await getUserDisplayNameFromLocalStore(page)).toBe(APPT_DISPLAY_NAME);
  });
});
