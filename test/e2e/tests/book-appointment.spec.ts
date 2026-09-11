import { test, expect, type Locator } from '@playwright/test';
import { BookingPage } from '../pages/booking-page';
import { DashboardPage } from '../pages/dashboard-page';
import { TBAcctsPage } from '../pages/tb-accts-page';
import {
  getTestPlatform,
  navigateToAppointmentAndSignIn,
  setDefaultUserSettingsLocalStore,
} from '../utils/utils';

import {
  APPT_BOOKEE_EMAIL,
  APPT_BOOKEE_NAME,
  APPT_DISPLAY_NAME,
  APPT_URL,
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  PLAYWRIGHT_TAG_PROD_SANITY,
  PLAYWRIGHT_TAG_STAGE_SANITY,
  TIMEOUT_10_SECONDS,
  TIMEOUT_30_SECONDS,
  TIMEOUT_60_SECONDS,
} from '../const/constants';

/**
 * This test must work in different timezones. Local browsers, BrowserStack
 * desktop browsers, and BrowserStack real devices can all report different
 * browser timezones. The public booking page renders slots in the booker's
 * browser timezone, which may differ from the Appointment account's timezone.
 *
 * After requesting a slot, the test reads the timezone shown on the booking
 * page and applies it to Appointment before looking for the new booking. This
 * lets the dashboard and booking page describe the requested time consistently.
 */
test.describe('book an appointment', () => {
  test('able to request a booking', {
    // Keep the union of the tags from the former desktop and mobile specs. The
    // regular mobile E2E tag is deliberately omitted because the old mobile
    // booking test ran only as part of the production mobile nightly suite.
    tag: [
      PLAYWRIGHT_TAG_PROD_SANITY,
      PLAYWRIGHT_TAG_E2E_SUITE,
      PLAYWRIGHT_TAG_PROD_NIGHTLY,
      PLAYWRIGHT_TAG_STAGE_SANITY,
      PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY,
    ],
  }, async ({ page }, testInfo) => {
    // Mobile real-device runs perform two complete sign-in flows and then poll
    // for asynchronous booking propagation. The suite-wide 150-second timeout
    // can expire before verifyEventCreated receives its intended two-minute
    // polling window, so give this unusually long end-to-end journey its own
    // five-minute budget on every platform.
    test.setTimeout(5 * TIMEOUT_60_SECONDS);

    const projectName = testInfo.project.name;
    const testPlatform = getTestPlatform(projectName);

    // Pass the original project name through to the page objects and sign-in
    // helper. They use it for existing platform-specific interaction handling:
    // Android sometimes requires forced clicks, while iOS does not support all
    // of Playwright's scrolling operations on the BrowserStack real device.
    const bookingPage = new BookingPage(page, projectName);
    const dashboardPage = new DashboardPage(page, projectName);
    const tbAcctsPage = new TBAcctsPage(page);

    if (testPlatform === 'desktop') {
      // Desktop projects depend on auth.desktop.setup.ts and therefore begin
      // with a saved, authenticated storage state. Mobile projects do not load
      // that state and naturally begin signed out. Explicitly log desktop out
      // so every platform exercises the same anonymous public-booking journey
      // and must provide the booker's name and email address.
      await page.goto(`${APPT_URL}logout`);

      // Appointment's OIDC logout redirects to Keycloak, which requires the
      // user to confirm the logout before following post_logout_redirect_uri
      // back to Appointment. Waiting for the button also ensures that the
      // redirect to Keycloak has completed before the test tries to continue.
      const keycloakLogoutButton = page.getByRole('button', { name: 'Logout', exact: true });
      await expect(keycloakLogoutButton).toBeVisible({ timeout: TIMEOUT_60_SECONDS });
      await keycloakLogoutButton.click();

      // Do not wait only for APPT_URL here. It is a transient stop in the
      // post-logout flow: Appointment immediately redirects from `/` to
      // `/login`, which then redirects to Keycloak. Starting the booking-page
      // navigation during that chain causes Firefox to report
      // NS_BINDING_ABORTED. The visible Keycloak Sign In button is the stable
      // signal that every logout redirect has completed.
      await expect(tbAcctsPage.signInButton).toBeVisible({ timeout: TIMEOUT_60_SECONDS });
    }

    // Use the week view to maximize the chance of finding an available slot.
    await bookingPage.gotoBookingPageWeekView();
    await expect(bookingPage.titleText).toBeVisible({ timeout: TIMEOUT_30_SECONDS });

    // Capture the timezone before selecting a slot. Android currently reports
    // GMT as `+00:00` (issue 1035), while Appointment expects an IANA timezone.
    let selectedSlotTimeZone = (
      await bookingPage.bookingPageTimeZoneFooter.innerText({ timeout: TIMEOUT_30_SECONDS })
    ).trim().split(': ')[1];

    if (selectedSlotTimeZone === '+00:00') {
      selectedSlotTimeZone = 'Europe/Dublin';
    }
    console.log(`bookee page is using timezone: ${selectedSlotTimeZone}`);

    // selectedSlot uses the DOM test-id format `event-YYYY-MM-DD HH:mm`.
    const selectedSlot = await bookingPage.selectAvailableBookingSlot(APPT_DISPLAY_NAME);
    console.log(`selected appointment time slot: ${selectedSlot}`);

    // All platforms are anonymous at this point, so use the same form-filling
    // path. BookingPage.finishBooking retains the Android forced-click workaround.
    await bookingPage.finishBooking(APPT_BOOKEE_NAME, APPT_BOOKEE_EMAIL);

    // window.scrollTo is supported by all targets and avoids the unsupported
    // scrollIntoViewIfNeeded operation on BrowserStack iOS.
    await page.evaluate(() => window.scrollTo(0, 0));

    // Submitting the form sends the booking request to the backend before the
    // success view is rendered. BrowserStack real devices can take noticeably
    // longer to complete that round trip, so wait generously for the actual UI
    // state instead of adding another unconditional delay.
    await expect(bookingPage.bookingRequestedTitleText).toBeVisible({ timeout: TIMEOUT_60_SECONDS });

    // Convert the selected DOM slot into the date/time format displayed by the
    // booking confirmation dialog and verify that the requested slot matches.
    const expectedSlotDate = await bookingPage.getDateFromSlotString(selectedSlot);
    const expectedSlotTime = await bookingPage.getStartTimeFromSlotString(selectedSlot);
    const expectedConfirmationDateTime = `${expectedSlotDate} from ${expectedSlotTime}`;
    console.log(`expect this time slot to be on the confirmation dialog: '${expectedConfirmationDateTime}'`);

    const confirmationDateTime: Locator = page.getByText(expectedConfirmationDateTime);
    await expect(confirmationDateTime).toBeVisible({ timeout: TIMEOUT_30_SECONDS });

    // Give the asynchronous booking creation a short head start before polling
    // the authenticated bookings list. verifyEventCreated performs the longer,
    // retrying wait for the new booking itself.
    await page.waitForTimeout(TIMEOUT_10_SECONDS);

    // Sign back in on the same platform, then align Appointment's timezone with
    // the public booking page so the bookings list renders the same wall-clock
    // time used to identify the selected slot.
    await navigateToAppointmentAndSignIn(page, projectName);
    await setDefaultUserSettingsLocalStore(page, selectedSlotTimeZone);
    await dashboardPage.verifyEventCreated(selectedSlot);
  });
});
