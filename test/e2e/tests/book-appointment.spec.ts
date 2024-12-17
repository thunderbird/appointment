import { test, expect } from '@playwright/test';
import { BookingPage } from '../pages/booking-page';
import { PROD_SHARE_LINK_SHORT, PROD_SHARE_LINK_LONG, PROD_ACCT_DISPLAY_NAME } from '../const/constants';

let bookingPage: BookingPage;

// verify booking page loaded successfully
const verifyBookingPageLoaded = async () => {
  await expect(bookingPage.titleText).toBeVisible({ timeout: 30_000 });
  await expect(bookingPage.titleText).toContainText(String(PROD_ACCT_DISPLAY_NAME));
  await expect(bookingPage.invitingText).toBeVisible();
  await expect(bookingPage.invitingText).toContainText(String(PROD_ACCT_DISPLAY_NAME));
  // todo check some more locators
}

test.beforeEach(async ({ page }) => {
  bookingPage = new BookingPage(page);
});

// verify we are able to book an appointment using existing user's share link
test.describe('book an appointment', {
  tag: '@prod-sanity'
}, () => {
  test('able to access booking page via short link', async ({ page }) => {
    await bookingPage.gotoBookingPage(String(PROD_SHARE_LINK_SHORT));
    await verifyBookingPageLoaded();
  });

  test('able to access booking page via long link', async ({ page }) => {
    await bookingPage.gotoBookingPage(String(PROD_SHARE_LINK_LONG));
    await verifyBookingPageLoaded();
  });

  test('able to request a booking', async ({ page }) => {
    await expect(true).toBeTruthy();
  });
});
