import { test, expect } from '@playwright/test';
import { BookingPage } from '../pages/booking-page';

import {
  APPT_DISPLAY_NAME,
  PLAYWRIGHT_TAG_PROD_SANITY,
  PLAYWRIGHT_TAG_E2E_SUITE,
  TIMEOUT_60_SECONDS,
  APPT_TIMEZONE_SETTING_PRIMARY,
  APPT_BOOKEE_NAME,
  APPT_BOOKEE_EMAIL,
  APPT_DASHBOARD_HOME_PAGE,
} from '../const/constants';

let bookingPage: BookingPage;

test.beforeEach(async ({ page }) => {
  bookingPage = new BookingPage(page);
});

// the share link (request a booking page) will display in the local browser context timezone but the main
// appointment account settings could be a different timezone (if so the test will fail to find the booked
// appointment since the time slot value will not match); set the browser context to always be in
// `America/Toronto` so the share link will be in the same timezone as the main account settings
test.use({
  timezoneId: APPT_TIMEZONE_SETTING_PRIMARY,
});

test.describe('dashboard pending requests link', () => {
  test('pending requests link appears after booking and navigates correctly', {
    tag: [PLAYWRIGHT_TAG_PROD_SANITY,PLAYWRIGHT_TAG_E2E_SUITE],
  }, async ({ page }) => {
    // Navigate to dashboard and verify no pending requests link initially
    await page.goto(APPT_DASHBOARD_HOME_PAGE);
    await expect(page.getByTestId('link-pending-requests')).not.toBeVisible();

    // Book an appointment
    await bookingPage.gotoBookingPageWeekView();
    await expect(bookingPage.titleText).toBeVisible({ timeout: TIMEOUT_60_SECONDS });

    // Select an available booking slot
    await bookingPage.selectAvailableBookingSlot(APPT_DISPLAY_NAME);

    // Now we have an availble booking time slot selected, click confirm button
    await bookingPage.confirmBtn.click();

    // Fill out booking form and submit
    await bookingPage.finishBooking(APPT_BOOKEE_NAME, APPT_BOOKEE_EMAIL);

    // by default after a slot is booked it requires confirmation from the host user first
    // 'boooking request sent' text appears twice, once in the pop-up and once in underlying page
    await expect(bookingPage.requestSentTitleText.first()).toBeVisible({ timeout: TIMEOUT_60_SECONDS });
    await expect(bookingPage.requestSentTitleText.nth(1)).toBeVisible();

    // Close the booking confirmation dialog
    await bookingPage.requestSentCloseBtn.click();

    // Go back to dashboard and check that pending requests link now appears
    await page.goto(APPT_DASHBOARD_HOME_PAGE);
    await expect(page.getByTestId('link-pending-requests')).toBeVisible();

    // Click the pending requests link and verify it navigates to the correct URL
    await page.getByTestId('link-pending-requests').click();
    await expect(page).toHaveURL(/.*\/bookings\?unconfirmed=true$/);
  });
});
