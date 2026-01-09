import { expect, type Page, type Locator } from '@playwright/test';
import { convertLongDate } from '../utils/utils';

import {
  APPT_BOOKINGS_PAGE,
  APPT_DASHBOARD_MONTH_PAGE,
  TIMEOUT_3_SECONDS,
} from '../const/constants';


export class DashboardPage {
  readonly page: Page;
  readonly navBarDashboardBtn: Locator;
  readonly userMenuAvatar: Locator;
  readonly logOutMenuItem: Locator;
  readonly firstDayOfWeekMonthView: Locator;
  readonly nextMonthArrow: Locator;
  readonly pendingBookingRequestsLink: Locator;

  constructor(page: Page) {
    this.page = page;
    this.navBarDashboardBtn = this.page.getByRole('link', { name: 'Dashboard' });
    this.userMenuAvatar = this.page.locator('.avatar regular');
    this.logOutMenuItem = this.page.getByTestId('user-nav-logout-menu');
    this.firstDayOfWeekMonthView = this.page.locator('.calendar-month__week-day-name').first();
    this.nextMonthArrow = this.page.locator('[data-icon="chevron-right"]');
    this.pendingBookingRequestsLink = this.page.getByTestId('link-pending-requests');
  }

  /**
   * Navigate to the bookings page so we can see all of our bookings
   */
  async gotoBookings() {
    // go to bookings page and set filter in URL to show confirmed only
    await this.page.goto(APPT_BOOKINGS_PAGE);
  }
 
  /**
   * Given a requested booking's time slot reference, verify that a corresponding event exists
   * in the host account's list of bookings. The bookings screen shows all bookings by default
   * (confirmed and unconfirmed) which is great because it is possible the test account could
   * have 'auto confirm' turned on.
   * @param slotDate String containing date of the requested slot (format 'October 29, 2025') as
   * provided by the booking request confirmation dialog at the time of requesting the slot.
   * @param slotTime String containg the time of the requested slot (format e.g: '03:30 PM') as
   * provided by the booking request confirmation dialog at the time of requesting the slot.
   */
  async verifyEventCreated(slotDate: string, slotTime: string) {
    // now wait a max of 2 minutes for the newly request appt to appear in the dashboard pending appts list
    await expect(async () => {
      await this.gotoBookings();
      await this.page.waitForTimeout(TIMEOUT_3_SECONDS);

      // the slot date is received in the format of 'February 17, 2025' but it needs to be in the format
      // of a string as MM/DD/YYYY (ie. 02/17/2025) to match the bookings list.
      const shortDate = await convertLongDate(slotDate);

      // the slot time is received in the format of `03:00 PM` but we need to drop the leading zero to
      // match the format on the bookings list
      if(slotTime[0] == '0') {
        slotTime = slotTime.slice(1);
      }

      // now we can build the event date, time string and search for it on the bookings list
      const eventString = `${shortDate}, ${slotTime}`;
      console.log(`searching bookings list for event: ${eventString}`);
      const apptLocator = this.page.getByRole('button', { name: eventString });
      await expect(apptLocator).toBeVisible();
    }).toPass({
      // Probe, wait 1s, probe, wait 2s, probe, wait 10s, probe, wait 10s, probe
      // ... Defaults to [100, 250, 500, 1000].
      intervals: [10_000, 10_000, 5_000],
      timeout: 120_000
    });
  }

  /**
   * Navigate to the dashboard month view
   */
  async gotoToDashboardMonthView() {
    await this.page.goto(APPT_DASHBOARD_MONTH_PAGE);
    await this.page.waitForTimeout(TIMEOUT_3_SECONDS);
  }
}
