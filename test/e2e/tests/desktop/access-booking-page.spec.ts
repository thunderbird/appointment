import { test, expect, type Page } from '@playwright/test';
import { BookingPage } from '../../pages/booking-page';
import { DashboardPage } from '../../pages/dashboard-page';

import {
  APPT_DISPLAY_NAME,
  PLAYWRIGHT_TAG_PROD_SANITY,
  TIMEOUT_60_SECONDS,
  APPT_TARGET_ENV,
  APPT_TIMEZONE_SETTING_PRIMARY,
  TIMEOUT_1_SECOND,
} from '../../const/constants';

var bookingPage: BookingPage;
var dashboardPage: DashboardPage;

// verify booking page loaded successfully
const verifyBookingPageLoaded = async (page: Page) => {
  await expect(bookingPage.titleText).toBeVisible({ timeout: TIMEOUT_60_SECONDS });
  await expect(bookingPage.titleText).toContainText(APPT_DISPLAY_NAME);
  await expect(bookingPage.bookATimeToMeetText).toBeVisible();
  await expect(bookingPage.bookATimeToMeetText).toContainText(APPT_DISPLAY_NAME);
  await expect(bookingPage.bookingCalendarHdrSun).toBeVisible();
  await expect(bookingPage.bookingCalendarHdrMon).toBeVisible();
  await expect(bookingPage.bookingCalendarHdrTue).toBeVisible();
  await expect(bookingPage.bookingCalendarHdrWed).toBeVisible();
  await expect(bookingPage.bookingCalendarHdrThu).toBeVisible();
  await expect(bookingPage.bookingCalendarHdrFri).toBeVisible();
  await expect(bookingPage.bookingCalendarHdrSat).toBeVisible();

  // verify calendar header
  const today: Date = new Date();
  const curMonth: string = today.toLocaleString('default', { month: 'short' });
  const curYear: string = String(today.getFullYear());

  // by default the booker page displays the current week; check week picker button
  // text is visible and contains correct month
  const currentDate = new Date();
  const monthName = currentDate.toLocaleString('default', { month: 'long' });
  expect(await bookingPage.bookingWeekPickerBtn.textContent()).toContain(monthName);

  // also the book appt button is hidden by default (since a slot is not yet selected)
  await page.waitForTimeout(TIMEOUT_1_SECOND);
  await expect(bookingPage.bookApptBtn).toBeHidden();
}

test.beforeEach(async ({ page }) => {
  bookingPage = new BookingPage(page);
  dashboardPage = new DashboardPage(page);
});

// the share link (request a booking page) will display in the local browser context timezone but the main
// appointment account settings could be a different timezone; set the browser context to always be in
// the primary timezone
test.use({
  timezoneId: APPT_TIMEZONE_SETTING_PRIMARY,
});

test.describe('access booking page on desktop browser', () => {
  test('able to access booking page via short link', {
    tag: [PLAYWRIGHT_TAG_PROD_SANITY],
  }, async ({ page }) => {
    await bookingPage.gotoBookingPageShortUrl();
    await verifyBookingPageLoaded(page);
  });

  test('able to access booking page via long link on desktop browser', {
    tag: [PLAYWRIGHT_TAG_PROD_SANITY]
  }, async ({ page }) => {
    // not supported on local dev env
    if (APPT_TARGET_ENV != 'dev') {
      await bookingPage.gotoBookingPageLongUrl();
      await verifyBookingPageLoaded(page);
    }
  });
});
