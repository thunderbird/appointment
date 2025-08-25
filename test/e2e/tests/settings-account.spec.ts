import { test, expect } from '@playwright/test';
import { SettingsPage } from '../pages/settings-page';
import { DashboardPage } from '../pages/dashboard-page';
import { AvailabilityPage } from '../pages/availability-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  APPT_MY_SHARE_LINK,
  APPT_AVAILABILITY_PAGE,
  TIMEOUT_1_SECOND,
  TIMEOUT_30_SECONDS,
  TIMEOUT_3_SECONDS,
 } from '../const/constants';
import { URL } from 'url';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;
let availabilityPage: AvailabilityPage;

test.describe('account settings', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    // note: we are already signed into Appointment with our default settings (via our auth-setup)
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);
    availabilityPage = new AvailabilityPage(page);

    // navigate to settings page, account settings section
    await settingsPage.gotoAccountSettings();
  });

  test('verify account settings', async ({ page }) => {
    // verify section header
    expect(settingsPage.accountSettingsHeader).toBeVisible();

    // verify booking page url displayed is correct
    await settingsPage.bookingPageURLInput.scrollIntoViewIfNeeded();
    const expUrl = new URL(APPT_MY_SHARE_LINK);
    const readUrl = new URL(await settingsPage.bookingPageURLInput.inputValue())
    expect(readUrl.origin).toEqual(expUrl.origin);
    expect(decodeURIComponent(readUrl.pathname)).toEqual(expUrl.pathname);

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
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
    expect(page.url()).toBe(APPT_AVAILABILITY_PAGE);
    await expect(availabilityPage.setAvailabilityText).toBeVisible();
  });
});
