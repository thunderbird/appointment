import { test, expect } from '@playwright/test';
import { BookingPage } from '../pages/booking-page';
import { DashboardPage } from '../pages/dashboard-page';
import { navigateToAppointmentProdAndSignIn } from '../utils/utils';
import { PROD_DISPLAY_NAME, APPT_BOOKING_REQUESTER_NAME, APPT_BOOKING_REQUESTER_EMAIL } from '../const/constants';

var bookingPage: BookingPage;
var dashboardPage: DashboardPage;

// verify booking page loaded successfully
const verifyBookingPageLoaded = async () => {
  await expect(bookingPage.titleText).toBeVisible({ timeout: 60_000 });
  await expect(bookingPage.titleText).toContainText(PROD_DISPLAY_NAME);
  await expect(bookingPage.invitingText).toBeVisible();
  await expect(bookingPage.invitingText).toContainText(PROD_DISPLAY_NAME);
  await expect(bookingPage.bookingCalendar).toBeVisible();
  // calendar header should contain current MMM YYYY
  const today: Date = new Date();
  const curMonth: string = today.toLocaleString('default', { month: 'short' });
  const curYear: string = String(today.getFullYear());
  await expect(bookingPage.calendarHeader).toHaveText(`${curMonth} ${curYear}`);
  // confirm button is disabled by default until a slot is selected
  await expect(bookingPage.confirmBtn).toBeDisabled();
}

test.beforeEach(async ({ page }) => {
  bookingPage = new BookingPage(page);
  dashboardPage = new DashboardPage(page);
});

// verify we are able to book an appointment using existing user's share link
test.describe('book an appointment', {
  tag: '@prod-sanity'
}, () => {
  test('able to access booking page via short link', async ({ page }) => {
    await bookingPage.gotoBookingPageShortUrl();
    await verifyBookingPageLoaded();
  });

  test('able to access booking page via long link', async ({ page }) => {
    await bookingPage.gotoBookingPageLongUrl();
    await verifyBookingPageLoaded();
  });

  test('able to request a booking', async ({ page }) => {
    // in order to ensure we find an available slot we can click on, first switch to week view URL
    await bookingPage.gotoBookingPageWeekView();
    await expect(bookingPage.titleText).toBeVisible({ timeout: 30_000 });

    // now select an available booking time slot  
    const selectedSlot: string|null = await bookingPage.selectAvailableBookingSlot(PROD_DISPLAY_NAME);
    console.log(`selected appointment time slot: ${selectedSlot}`);

    // now we have an availble booking time slot selected, click confirm button
    await bookingPage.confirmBtn.click();

    // now fill out the book selection dialog with booking requester's info and book it
    await bookingPage.finishBooking(APPT_BOOKING_REQUESTER_NAME, APPT_BOOKING_REQUESTER_EMAIL);

    // 'boooking request sent' text appears twice, once in the pop-up and once in underlying page
    await expect(bookingPage.requestSentTitleText.first()).toBeVisible({ timeout: 60_000 });
    await expect(bookingPage.requestSentTitleText.nth(1)).toBeVisible();

    // booking request sent dialog availability text contains correct user name
    // this text also appears twice, once in the pop-up and once in underlying page
    await expect(bookingPage.requestSentAvailabilityText.first()).toBeVisible();
    await expect(bookingPage.requestSentAvailabilityText.nth(1)).toBeVisible();
    const expectedText: string = `${PROD_DISPLAY_NAME}'s Availability`;
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

    // navigate to and sign into appointment (host account whom we requested a booking with/owns the share link)
    await navigateToAppointmentProdAndSignIn(page);

    // now verify a 'hold' now exists on the host calendar at the time slot that was requested
    await dashboardPage.verifyHoldEventCreated(selectedSlot, PROD_DISPLAY_NAME, APPT_BOOKING_REQUESTER_NAME);
  });
});
