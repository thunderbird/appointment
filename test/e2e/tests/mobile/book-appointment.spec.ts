import { test, expect } from '@playwright/test';
import { BookingPage } from '../../pages/booking-page';
import { DashboardPage } from '../../pages/dashboard-page';
import { ensureWeAreSignedIn } from '../../utils/utils';

import {
  APPT_DISPLAY_NAME,
  PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY,
  PLAYWRIGHT_TAG_E2E_SUITE_MOBILE,
  APPT_BOOKEE_NAME,
  APPT_BOOKEE_EMAIL,  
  TIMEOUT_3_SECONDS,
  TIMEOUT_10_SECONDS,
  TIMEOUT_30_SECONDS,
  TIMEOUT_60_SECONDS,
} from '../../const/constants';

var bookingPage: BookingPage;
var dashboardPage: DashboardPage;

test.beforeEach(async ({ page }, testInfo) => {
  bookingPage = new BookingPage(page, testInfo.project.name); // i.e. 'ios-safari'
  dashboardPage = new DashboardPage(page);
});


test.describe('book an appointment on mobile browser', () => {

  test('able to request a booking on mobile browser', {
    tag: [PLAYWRIGHT_TAG_E2E_SUITE_MOBILE, PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY],
  }, async ({ page }) => {
    // in order to ensure we find an available slot we can click on, first switch to week view URL
    await bookingPage.gotoBookingPageWeekView();
    await expect(bookingPage.titleText).toBeVisible({ timeout: TIMEOUT_30_SECONDS });

    // now select an available booking time slot  
    const selectedSlot: string|null = await bookingPage.selectAvailableBookingSlot(APPT_DISPLAY_NAME);
    console.log(`selected appointment time slot: ${selectedSlot}`);

    // now provide the bookee details for our selected time slot; when signed into Appointment this
    // info is provided automatically however for this test we are selecting a time slot without being
    // signed in / without being an Appointment user; so we must specify the bookee name and email
    // also after entering bookee details, this clicks the 'book appointment' button to request the slot
    await bookingPage.finishBooking(APPT_BOOKEE_NAME, APPT_BOOKEE_EMAIL);

    // verify booking request sent pop-up
    await expect(bookingPage.bookingConfirmedTitleText.first()).toBeVisible({ timeout: TIMEOUT_60_SECONDS });
    await bookingPage.scrollIntoView(bookingPage.bookingConfirmedTitleText);

    // booking request sent dialog should display the correct time slot that was requested
    // our requested time slot is stored in this format, as example: 'event-2025-01-14 14:30'
    // the dialog reports the slot in this format, as example: 'January 14, 2025' with start time
    // on next line; convert our selected slot value to same format as displayed so we can verify
    const expDateStr = await bookingPage.getDateFromSlotString(selectedSlot);
    const expTimeStr = await bookingPage.getTimeFromSlotString(selectedSlot);

    // now verify the correct date/time is dispalyed on the booking request sent pop-up
    await bookingPage.verifyRequestedSlotTextDisplayed(expDateStr, expTimeStr);  

    // now verify a corresponding pending booking was created on the host account's list of pending bookings
    // wait N seconds for the appointment dashboard to update, sometimes the test is so fast when it
    // switches back to the dashboard the new pending appointment hasn't been added/displayed yet
    await page.waitForTimeout(TIMEOUT_10_SECONDS);
    await ensureWeAreSignedIn(page);
    await dashboardPage.verifyEventCreated(expDateStr, expTimeStr);

    // also go back to main dashboard and check that pending requests link now appears
    await dashboardPage.gotoToDashboardMonthView();
    await expect(dashboardPage.pendingBookingRequestsLink).toBeVisible();

    // click the pending requests link and verify it navigates to the correct URL
    await dashboardPage.pendingBookingRequestsLink.click();
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
    await expect(page).toHaveURL(/.*\/bookings\?unconfirmed=true/);
  });
});
