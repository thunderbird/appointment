import { test, expect, Locator } from '@playwright/test';
import { BookingPage } from '../../pages/booking-page';
import { DashboardPage } from '../../pages/dashboard-page';
import { navigateToAppointmentAndSignIn, setDefaultUserSettingsLocalStore } from '../../utils/utils';

import {
  APPT_DISPLAY_NAME,
  PLAYWRIGHT_TAG_PROD_SANITY,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  PLAYWRIGHT_TAG_E2E_DESKTOP_SUITE,
  TIMEOUT_30_SECONDS,
  TIMEOUT_60_SECONDS,
  TIMEOUT_3_SECONDS,
  TIMEOUT_10_SECONDS,
} from '../../const/constants';

var bookingPage: BookingPage;
var dashboardPage: DashboardPage;

test.beforeEach(async ({ page }) => {
  bookingPage = new BookingPage(page);
  dashboardPage = new DashboardPage(page);
});

/**
 * The test must be able to run in different timezones because people may run this on their local machine, and also
 * when the test runs in CI on BrowserStack it is in a different timezone, and when run on BrowserStack real mobile devices
 * the device can be set in yet another different timezone.
 *
 * The E2E tests ensure the Appointment timezone setting itself is always set to APPT_TIMEZONE_SETTING_PRIMARY on test
 * startup, however the boookee page (when selecting timeslots) is displayed in the local broweser timezone which
 * may not match the Appointment application's timezone setting.
 *
 * To get around that, when the booking page is loaded (to select a time slot) the test grabs the timezone displayed at
 * the bottom of the page. After a time slot is selected the test verifies the confirmed appointment request dialog. Then
 * when signing in to the Appointment dashboard to confirm that a corresponding pending appointment was created, the test
 * will change the Appointment app timezone setting to match the timezone of our selected time slot/bookee page, so it
 * can easily find the pending appointment that matches the selected timeslot.
 */
test.describe('book an appointment on desktop browser', () => {

  test('able to request a booking on desktop browser', {
    tag: [PLAYWRIGHT_TAG_PROD_SANITY, PLAYWRIGHT_TAG_E2E_DESKTOP_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
  }, async ({ page }) => {
    // in order to ensure we find an available slot we can click on, first switch to week view URL
    await bookingPage.gotoBookingPageWeekView();
    await expect(bookingPage.titleText).toBeVisible({ timeout: TIMEOUT_30_SECONDS });

    // record the timezone that the bookee page is using (timezone of selected time slot)
    const selectedSlotTimeZone = (await bookingPage.bookingPageTimeZoneFooter.innerText()).trim().split(': ')[1];
    console.log(`bookee page is using timezone: ${selectedSlotTimeZone}`);

    // now select an available booking time slot
    // selectedSlot is in the format of 'event-2026-01-22 15:00'
    const selectedSlot: string|null = await bookingPage.selectAvailableBookingSlot(APPT_DISPLAY_NAME);
    console.log(`selected appointment time slot: ${selectedSlot}`);

    // now we have an availble booking time slot selected, click confirm button
    await bookingPage.bookApptBtn.click();

    // verify booking request sent pop-up
    await expect(bookingPage.bookingConfirmedTitleText.first()).toBeVisible({ timeout: TIMEOUT_60_SECONDS });
    await bookingPage.bookingConfirmedTitleText.first().scrollIntoViewIfNeeded();

    // booking request sent dialog should display the correct time slot that was requested
    // our requested time slot is stored in this format, as example: 'event-2026-01-22 15:00'
    // the dialog reports the slot in this format: 'Thu, Jan 22 from 03:00pm'
    // convert our selected slot value to same format as displayed so we can verify
    const expSlotDateStr = await bookingPage.getDateFromSlotString(selectedSlot);
    const expSlotTimeStr = await bookingPage.getStartTimeFromSlotString(selectedSlot);
    const expConfirmDateTimeStr = `${expSlotDateStr} from ${expSlotTimeStr}`;

    // now verify the correct date/time is dispalyed on the booking request sent pop-up 
    console.log(`expect this time slot to be on the confirmation dialog: '${expConfirmDateTimeStr}'`);
    const confirmDateDisplayText: Locator = page.getByText(expConfirmDateTimeStr);
    await expect(confirmDateDisplayText).toBeVisible({ timeout: TIMEOUT_30_SECONDS });

    // now verify a corresponding pending booking was created on the host account's list of pending bookings
    // give some initial time for the new confirmed appointment to make it to the Appointment dashboard sometimes the
    // test is so fast when it switches back to the dashboard the new appointment hasn't been added/displayed yet
    await page.waitForTimeout(TIMEOUT_10_SECONDS);
    // now verify a corresponding booking was created on the host account's list of bookings; if we aren't already signed
    // into Appointment then sign in to the main dashboard first; then setDefaultUserSettinsLocalStore will set the
    // Appointment timezone setting to match the timezone that was used by the booking page; so that we can easily find the
    // selected time slot in the list of confirmed Appointment bookings
    await navigateToAppointmentAndSignIn(page);
    await setDefaultUserSettingsLocalStore(page, selectedSlotTimeZone);
    await dashboardPage.verifyEventCreated(selectedSlot);

    // also go back to main dashboard and check that pending requests link now appears
    await dashboardPage.gotoToDashboardMonthView();
    await expect(dashboardPage.pendingBookingRequestsLink).toBeVisible();

    // click the pending requests link and verify it navigates to the correct URL
    await dashboardPage.pendingBookingRequestsLink.click();
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
    await expect(page).toHaveURL(/.*\/bookings\?unconfirmed=true/);
  });
});
