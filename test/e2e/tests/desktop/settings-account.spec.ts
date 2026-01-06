import { test, expect } from '@playwright/test';
import { SettingsPage } from '../../pages/settings-page';
import { DashboardPage } from '../../pages/dashboard-page';
import { AvailabilityPage } from '../../pages/availability-page';
import { BookingPage } from '../../pages/booking-page';
import { ensureWeAreSignedIn } from '../../utils/utils';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  APPT_DISPLAY_NAME,
  APPT_MY_SHARE_LINK,
  TIMEOUT_1_SECOND,
  TIMEOUT_30_SECONDS,
 } from '../../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;
let availabilityPage: AvailabilityPage;
let bookApptPage: BookingPage;

test.describe('account settings on desktop browser', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    await ensureWeAreSignedIn(page);
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);
    availabilityPage = new AvailabilityPage(page);
    bookApptPage = new BookingPage(page);

    // navigate to settings page, account settings section
    await settingsPage.gotoAccountSettings();
  });

  test('verify account settings on desktop browser', async ({ page }) => {
    // verify section header
    await expect(settingsPage.accountSettingsHeader).toBeVisible();

    // verify display name displayed is as expected
    await expect(settingsPage.displayNameInput).toBeVisible();
    expect(await settingsPage.displayNameInput.inputValue()).toBe(APPT_DISPLAY_NAME);

    // verify booking page url displayed is correct
    await settingsPage.bookingPageURLInput.scrollIntoViewIfNeeded();
    expect(await settingsPage.bookingPageURLInput.inputValue()).toBe(APPT_MY_SHARE_LINK);

    // ensure we can click the copy link button; note: we can't access clipboard in firefox b/c of security
    await settingsPage.scrollIntoView(settingsPage.copyLinkBtn);
    await expect(settingsPage.copyLinkBtn).toBeEnabled();
    await settingsPage.copyLinkBtn.click();

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
});
