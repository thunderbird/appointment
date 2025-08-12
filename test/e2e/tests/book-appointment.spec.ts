import { test, expect } from '@playwright/test';
import { BookingPage } from '../pages/booking-page';
import { DashboardPage } from '../pages/dashboard-page';

import {
  APPT_DISPLAY_NAME,
  APPT_BOOKEE_NAME,
  APPT_BOOKEE_EMAIL,
  PLAYWRIGHT_TAG_PROD_SANITY,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  PLAYWRIGHT_TAG_E2E_SUITE,
  TIMEOUT_15_SECONDS,
  TIMEOUT_30_SECONDS,
  TIMEOUT_60_SECONDS,
  APPT_TIMEZONE_SETTING_PRIMARY,
  TIMEOUT_3_SECONDS,
} from '../const/constants';

var bookingPage: BookingPage;
var dashboardPage: DashboardPage;

test.beforeEach(async ({ page }) => {
  bookingPage = new BookingPage(page);
  dashboardPage = new DashboardPage(page);
});

// the share link (request a booking page) will display in the local browser context timezone but the main
// appointment account settings could be a different timezone (if so the test will fail to find the booked
// appointment since the time slot value will not match); set the browser context to always be in
// `America/Toronto` so the share link will be in the same timezone as the main account settings
test.use({
  timezoneId: APPT_TIMEZONE_SETTING_PRIMARY,
});

test.describe('book an appointment', () => {

  test('able to request a booking', {
    tag: [PLAYWRIGHT_TAG_PROD_SANITY, PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
  }, async ({ page }) => {
    // in order to ensure we find an available slot we can click on, first switch to week view URL
    await bookingPage.gotoBookingPageWeekView();
    await expect(bookingPage.titleText).toBeVisible({ timeout: TIMEOUT_30_SECONDS });

    // now select an available booking time slot  
    const selectedSlot: string|null = await bookingPage.selectAvailableBookingSlot(APPT_DISPLAY_NAME);
    console.log(`selected appointment time slot: ${selectedSlot}`);

    // now we have an availble booking time slot selected, click confirm button
    await bookingPage.confirmBtn.click();

    // now fill out the book selection dialog with booking requester's info and book it
    await bookingPage.finishBooking(APPT_BOOKEE_NAME, APPT_BOOKEE_EMAIL);

    // by default after a slot is booked it requires confirmation from the host user first
    // 'boooking request sent' text appears twice, once in the pop-up and once in underlying page
    await expect(bookingPage.requestSentTitleText.first()).toBeVisible({ timeout: TIMEOUT_60_SECONDS });
    await expect(bookingPage.requestSentTitleText.nth(1)).toBeVisible();

    // booking request sent dialog availability text contains correct user name
    // this text also appears twice, once in the pop-up and once in underlying page
    await expect(bookingPage.requestSentAvailabilityText.first()).toBeVisible();
    await expect(bookingPage.requestSentAvailabilityText.nth(1)).toBeVisible();
    const expectedText: string = `${APPT_DISPLAY_NAME}'s Availability`;
    expect(bookingPage.requestSentAvailabilityText.first()).toContainText(expectedText);
    expect(bookingPage.requestSentAvailabilityText.nth(1)).toContainText(expectedText);

    // booking request sent dialog should display the correct time slot that was requested
    // our requested time slot is stored in this format, as example: 'event-2025-01-14 14:30'
    // the dialog reports the slot in this format, as example: 'Tuesday, January 14, 2025 02:30 PM'
    // first convert our selected slot value to same format as displayed so we can verify
    const expDateStr = await bookingPage.getDateFromSlotString(selectedSlot);
    const expTimeStr = await bookingPage.getTimeFromSlotString(selectedSlot);

    // now verify the correct date/time is dispalyed on the booking request sent pop-up
    await bookingPage.verifyRequestedSlotTextDisplayed(expDateStr, expTimeStr);  

    // now close out the 'booking request sent' pop-up dialog
    await bookingPage.requestSentCloseBtn.click();

    // note: we are already signed into Appointment (via our auth-setup)

    // now verify a corresponding pending booking was created on the host account's list of pending bookings
    // (drop the day of the week from our time slot string as this function just needs the month, day, and year)
    const expMonthDayYear = expDateStr.substring(expDateStr.indexOf(',') + 2);
    // wait N seconds for the appointment dashboard to update, sometimes the test is so fast when it
    // switches back to the dashboard the new pending appointment hasn't been added/displayed yet
    await page.waitForTimeout(TIMEOUT_15_SECONDS);
    await dashboardPage.verifyEventCreated(APPT_DISPLAY_NAME, APPT_BOOKEE_NAME, expMonthDayYear, expTimeStr);

    // also go back to main dashboard and check that pending requests link now appears
    await dashboardPage.gotoToDashboardMonthView();
    await expect(dashboardPage.pendingBookingRequestsLink).toBeVisible();

    // click the pending requests link and verify it navigates to the correct URL
    await dashboardPage.pendingBookingRequestsLink.click();
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
    await expect(page).toHaveURL(/.*\/bookings\?unconfirmed=true/);
  });
});
