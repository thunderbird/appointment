import { test, expect } from '@playwright/test';
import { BookingPage } from '../pages/booking-page';
import { DashboardPage } from '../pages/dashboard-page';

import {
  APPT_DISPLAY_NAME,
  PLAYWRIGHT_TAG_PROD_SANITY,
  PLAYWRIGHT_TAG_PROD_NIGHTLY_MOBILE,
  TIMEOUT_60_SECONDS,
  APPT_TARGET_ENV,
  APPT_TIMEZONE_SETTING_PRIMARY,
} from '../const/constants';

var bookingPage: BookingPage;
var dashboardPage: DashboardPage;

// verify booking page loaded successfully
const verifyBookingPageLoaded = async () => {
  await expect(bookingPage.titleText).toBeVisible({ timeout: TIMEOUT_60_SECONDS });
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

// the share link (request a booking page) will display in the local browser context timezone but the main
// appointment account settings could be a different timezone (if so the test will fail to find the booked
// appointment since the time slot value will not match); set the browser context to always be in
// `America/Toronto` so the share link will be in the same timezone as the main account settings
test.use({
  timezoneId: APPT_TIMEZONE_SETTING_PRIMARY,
});

test.describe('access booking page', () => {
  test('able to access booking page via short link', {
    tag: [PLAYWRIGHT_TAG_PROD_SANITY, PLAYWRIGHT_TAG_PROD_NIGHTLY_MOBILE],
  }, async ({ page }) => {
    await bookingPage.gotoBookingPageShortUrl();
    await verifyBookingPageLoaded();
  });

  test('able to access booking page via long link', {
    tag: [PLAYWRIGHT_TAG_PROD_SANITY]
  }, async ({ page }) => {
    // not supported on local dev env
    if (APPT_TARGET_ENV != 'dev') {
      await bookingPage.gotoBookingPageLongUrl();
      await verifyBookingPageLoaded();
    }
  });
});
