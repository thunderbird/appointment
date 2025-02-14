import { test, expect } from '@playwright/test';
import { BookingPage } from '../pages/booking-page';
import { DashboardPage } from '../pages/dashboard-page';
import { navigateToAppointmentAndSignIn } from '../utils/utils';
import { APPT_TARGET_ENV, APPT_DISPLAY_NAME, APPT_BOOKING_REQUESTER_NAME, APPT_BOOKING_REQUESTER_EMAIL } from '../const/constants';

var bookingPage: BookingPage;
var dashboardPage: DashboardPage;

// verify booking page loaded successfully
const verifyBookingPageLoaded = async () => {
  await expect(bookingPage.titleText).toBeVisible({ timeout: 60_000 });
  await expect(bookingPage.titleText).toContainText(APPT_DISPLAY_NAME);
  await expect(bookingPage.invitingText).toBeVisible();
  await expect(bookingPage.invitingText).toContainText(APPT_DISPLAY_NAME);
  await expect(bookingPage.bookingCalendar).toBeVisible();

  // verify calendar header
  const today: Date = new Date();
  const curMonth: string = today.toLocaleString('default', { month: 'short' });
  const curYear: string = String(today.getFullYear());

  // by default you can only book slots 1-14 days in the future; if it's near the end of the
  // month then there's a chance there are no slots availble to be booked; the booking request
  // page always shows the month that has the first available time slot; so the month displayed
  // may be the current month or one month in the future (and perhaps next year if January)

  // the header may contain either the current month or the next month
  today.setMonth(today.getMonth() + 1, 1);
  const nextMonth = today.toLocaleString('default', { month: 'short' });
  const monthRegex = new RegExp(String.raw`${curMonth}|${nextMonth}`);
  await expect(bookingPage.calendarHeader).toContainText(monthRegex);

  // if the current month is Dec then the displayed month might be Jan, which means in that case
  // the year value might be this year or next year; for other months it's safe to check for
  // the current year only because the test may book appointments in current or +1 month only
  if (curMonth == 'Dec') {
    const nextYear = curYear + 1;
    var yearRegex = new RegExp(String.raw`... ${curYear}|${nextYear}`);
  } else {
    var yearRegex = new RegExp(String.raw`... ${curYear}`);
  }
  await expect(bookingPage.calendarHeader).toContainText(yearRegex);

  // also the confirm button is disabled by default until a slot is selected
  await expect(bookingPage.confirmBtn).toBeDisabled();
}

test.beforeEach(async ({ page }) => {
  bookingPage = new BookingPage(page);
  dashboardPage = new DashboardPage(page);
});

// verify we are able to book an appointment using existing user's share link
test.describe('book an appointment', () => {
  test('able to access booking page via short link', {
    tag: '@prod-sanity',
  }, async ({ page }) => {
    await bookingPage.gotoBookingPageShortUrl();
    await verifyBookingPageLoaded();
  });

  test('able to access booking page via long link', {
    tag: '@prod-sanity',
  }, async ({ page }) => {
    await bookingPage.gotoBookingPageLongUrl();
    await verifyBookingPageLoaded();
  });

  test('able to request a booking', {
    tag: ['@prod-sanity', '@e2e-suite'],
  }, async ({ page }) => {
    // in order to ensure we find an available slot we can click on, first switch to week view URL
    await bookingPage.gotoBookingPageWeekView();
    await expect(bookingPage.titleText).toBeVisible({ timeout: 30_000 });

    // now select an available booking time slot  
    const selectedSlot: string|null = await bookingPage.selectAvailableBookingSlot(APPT_DISPLAY_NAME);
    console.log(`selected appointment time slot: ${selectedSlot}`);

    // now we have an availble booking time slot selected, click confirm button
    await bookingPage.confirmBtn.click();

    // now fill out the book selection dialog with booking requester's info and book it
    await bookingPage.finishBooking(APPT_BOOKING_REQUESTER_NAME, APPT_BOOKING_REQUESTER_EMAIL);

    if (APPT_TARGET_ENV == 'dev') {
      // when running against local dev environment after a slot is booked it doesn't require
      // confirmation by the host user, so the event is automatically booked and the title text
      // will be different to reflect that the appointment is booked (not pending/requested)
      await expect(bookingPage.eventBookedTitleText).toBeVisible({ timeout: 60_000 });
    } else {
      // in production and stage after a slot is booked it requires confirmation from the host user first
      // 'boooking request sent' text appears twice, once in the pop-up and once in underlying page
      await expect(bookingPage.requestSentTitleText.first()).toBeVisible({ timeout: 60_000 });
      await expect(bookingPage.requestSentTitleText.nth(1)).toBeVisible();
    }

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

    // navigate to and sign into appointment (host account whom we requested a booking with/owns the share link)
    await navigateToAppointmentAndSignIn(page);

    // now verify a corresponding pending booking was created on the host account's list of pending bookings
    // (drop the day of the week from our time slot string as this function just needs the month, day, and year)
    const expMonthDayYear = expDateStr.substring(expDateStr.indexOf(',') + 2);
    await dashboardPage.verifyEventCreated(APPT_DISPLAY_NAME, APPT_BOOKING_REQUESTER_NAME, expMonthDayYear, expTimeStr);
  });
});
