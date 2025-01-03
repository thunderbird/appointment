import { test, expect } from '@playwright/test';
import { BookingPage } from '../pages/booking-page';
import { PROD_DISPLAY_NAME, APPT_PROD_MY_SHARE_LINK } from '../const/constants';
import { APPT_PROD_SHORT_SHARE_LINK_PREFIX, APPT_PROD_LONG_SHARE_LINK_PREFIX } from '../const/constants';

let bookingPage: BookingPage;

// verify booking page loaded successfully
const verifyBookingPageLoaded = async () => {
  await expect(bookingPage.titleText).toBeVisible({ timeout: 30_000 });
  await expect(bookingPage.titleText).toContainText(PROD_DISPLAY_NAME);
  await expect(bookingPage.invitingText).toBeVisible();
  await expect(bookingPage.invitingText).toContainText(PROD_DISPLAY_NAME);
  await expect(bookingPage.bookingCalendar).toBeVisible();
  // calendar header should contain current MMM YYYY
  let today = new Date();
  let curMonth = today.toLocaleString('default', { month: 'short' });
  var curYear = String(today.getFullYear());
  await expect(bookingPage.calendarHeader).toHaveText(`${curMonth} ${curYear}`);
  // confirm button is disabled by default until a slot is selected
  await expect(bookingPage.confirmButton).toBeDisabled();
}

test.beforeEach(async ({ page }) => {
  bookingPage = new BookingPage(page);
});

// verify we are able to book an appointment using existing user's share link
test.describe('book an appointment', {
  tag: '@prod-sanity'
}, () => {
  test('able to access booking page via short link', async ({ page }) => {
    await bookingPage.gotoBookingPage(APPT_PROD_MY_SHARE_LINK);
    await verifyBookingPageLoaded();
  });

  test('able to access booking page via long link', async ({ page }) => {
    // the share link is short by default; build the corresponding long link first
    let prodShareLinkUser: string = APPT_PROD_MY_SHARE_LINK.split(APPT_PROD_SHORT_SHARE_LINK_PREFIX)[1];
    let prodShareLinkLong: string = `${APPT_PROD_LONG_SHARE_LINK_PREFIX}${prodShareLinkUser}`;
    await bookingPage.gotoBookingPage(prodShareLinkLong);
    await verifyBookingPageLoaded();
  });

  test('able to request a booking', async ({ page }) => {
    await bookingPage.gotoBookingPage(APPT_PROD_MY_SHARE_LINK);

    // by default we arrive on month view; if it happens to be the end of the month there may not
    // be any available appointment slots and we may need to go forward to the next month, but
    // let's first check for a specific slot (?)
    // this fails and says multi available
    //await expect(page.getByText('9:00 AM - 09:30 AM')).toBeVisible();
    // these work - and result is the specific time slot is selected
    await expect(page.locator('[id="calendar-month__event-2025-01-08\\ 09\\:002025-01-08"]').getByText('9:00 AM - 09:30 AM'))
      .toBeVisible();
    await page.locator('[id="calendar-month__event-2025-01-08\\ 09\\:002025-01-08"]').getByText('9:00 AM - 09:30 AM')
      .click();
    // move above into bookingPage also; may need to get current date and then get next upcoming weekday? and get that slot?

    await bookingPage.confirmButton.click();
  });
});
