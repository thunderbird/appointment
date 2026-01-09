import { test, expect } from '@playwright/test';
import { BookingPage } from '../../pages/booking-page';
import { DashboardPage } from '../../pages/dashboard-page';
import { mobileSignInAndSetup } from '../../utils/utils';

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
  TIMEOUT_2_SECONDS,
} from '../../const/constants';

var bookingPage: BookingPage;
var dashboardPage: DashboardPage;
var testProjectName: string;


/**
 * The test must be able to run from different timezones because people may run this on their local machine, and also
 * when the test runs in CI on BrowserStack it is in a different timezone, and when run on BrowserStack real mobile devices
 * the device can be set in yet another different timezone. In order to get around that we ensure that the Appointment
 * application timezone setting matches the timezone where the booking page is displayed, as follows.
 * When the booking page is loaded (to select a time slot) the test grabs the timezone displayed at the bottom of the page.
 * After a time slot is selected the test verifies that same timezone is displayed in the confirmed appointment dialog.
 * Then when confirming the corresponding event is created in Appointment, the test signs into Appointment and then sets
 * the Appointment timezone setting to match the time zone of the booking page; then when searching for a confirmed booking
 * that matches the selected time slot, the list of bookings matches the timezone that was used when the slot was selected.
 */
test.describe('book an appointment on mobile browser', () => {

  test.beforeEach(async ({ page }, testInfo) => {
    bookingPage = new BookingPage(page, testInfo.project.name); // i.e. 'ios-safari'
    dashboardPage = new DashboardPage(page);
    testProjectName = testInfo.project.name;
  });

  test('able to request a booking on mobile browser', {
    tag: [PLAYWRIGHT_TAG_E2E_SUITE_MOBILE, PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY],
  }, async ({ page }) => {
    // in order to ensure we find an available slot we can click on, first switch to week view URL
    await bookingPage.gotoBookingPageWeekView();
    await expect(bookingPage.titleText).toBeVisible({ timeout: TIMEOUT_30_SECONDS });

    // record the timezone that the booking page is using (will be the timezone of selected time slot)
    // issue 1035 causes the timezone to be read by the Appointment booking page on android as "+00:00"; check
    // if that is the retrieved timezone value from the booking page and if so use "UTC" instead
    var selectedSlotTimeZone = (await bookingPage.bookingPageTimeZoneFooter.innerText()).split(': ')[1].trim();
    if (selectedSlotTimeZone == '+00:00')
      selectedSlotTimeZone = 'UTC';
    console.log(`booking page is using time zone: ${selectedSlotTimeZone}`);

    // now select an available booking time slot  
    const selectedSlot: string|null = await bookingPage.selectAvailableBookingSlot(APPT_DISPLAY_NAME);
    console.log(`selected appointment time slot: ${selectedSlot}`);

    // now provide the bookee details for our selected time slot; when signed into Appointment this
    // info is provided automatically however for this test we are selecting a time slot without being
    // signed in / without being an Appointment user; so we must specify the bookee name and email
    // also after entering bookee details, this clicks the 'book appointment' button to request the slot
    await bookingPage.finishBooking(APPT_BOOKEE_NAME, APPT_BOOKEE_EMAIL);

    // verify booking request sent pop-up
    // on iOS we currently have to scroll to top of page first to see the confirmation
    // we can remove the scrolling to top once issue #1423 is resolved
    page.evaluate("window.scrollTo(0, 0)")
    page.waitForTimeout(TIMEOUT_2_SECONDS);
    await expect(bookingPage.bookingConfirmedTitleText.first()).toBeVisible({ timeout: TIMEOUT_60_SECONDS });
    await bookingPage.scrollIntoView(bookingPage.bookingConfirmedTitleText);

    // booking request sent dialog should display the correct time slot that was requested
    // our requested time slot is stored in this format, as example: 'event-2025-01-14 14:30'
    // the dialog reports the slot in this format, as example: 'January 14, 2025' with start time
    // on next line; convert our selected slot value to same format as displayed so we can verify
    const expDateStr = await bookingPage.getDateFromSlotString(selectedSlot);
    const expTimeStr = await bookingPage.getTimeFromSlotString(selectedSlot);

    // now verify the correct date/time is dispalyed on the booking confirmed dialog
    await bookingPage.verifyRequestedSlotTextDisplayed(expDateStr, expTimeStr, selectedSlotTimeZone);

    // give some initial time for the new confirmed appointment to make it to the Appointment dashboard sometimes the
    // test is so fast when it switches back to the dashboard the new appointment hasn't been added/displayed yet
    await page.waitForTimeout(TIMEOUT_10_SECONDS);

    // now verify a corresponding booking was created on the host account's list of bookings; on mobile we aren't signed
    // into Apppointment yet, so sign in to the main dashboard first; mobileSignInAndSetup will then set the Appointment
    // settings timezone to match the timezone that was used by the booking page; so that we can easily find the selected
    // time slot in the list of confirmed Appointment bookings
    await mobileSignInAndSetup(page, testProjectName, selectedSlotTimeZone);
    await dashboardPage.verifyEventCreated(expDateStr, expTimeStr);

    // also go back to main dashboard and check that pending requests link now appears
    await dashboardPage.gotoToDashboardMonthView();
    await expect(dashboardPage.pendingBookingRequestsLink).toBeVisible();
  });
});
