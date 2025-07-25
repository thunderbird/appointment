import { expect, type Page, type Locator } from '@playwright/test';

import {
  APPT_PENDING_BOOKINGS_PAGE,
  APPT_BOOKED_BOOKINGS_PAGE,
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

  constructor(page: Page) {
    this.page = page;
    this.navBarDashboardBtn = this.page.getByRole('link', { name: 'Dashboard' });
    this.userMenuAvatar = this.page.getByTestId('user-menu-avatar');
    this.logOutMenuItem = this.page.getByTestId('user-nav-logout-menu');
    this.firstDayOfWeekMonthView = this.page.locator('.calendar-month__week-day-name').first();
    this.nextMonthArrow = this.page.locator('[data-icon="chevron-right"]');
  }

  /**
   * Navigate to the pending bookings page and display all future pending bookings
   */
  async gotoPendingBookings() {
    // go to bookings page and set filter in URL to show pending only
    await this.page.goto(APPT_PENDING_BOOKINGS_PAGE);
  }

  /**
   * Navigate to the booked bookings page and display all confirmed/booked bookings
   */
  async gotoBookedBookings() {
    // go to bookings page and set filter in URL to show confirmed only
    await this.page.goto(APPT_BOOKED_BOOKINGS_PAGE);
  }
 
  /**
   * Given a requested booking's time slot reference, verify that a corresponding event exists
   * in the host account's list of bookings. If the host user's `Booking Confirmation` setting
   * is enabled (which is the default), then the created appointment will be pending (HOLD) as
   * it needs to be confirmed; but if the `Booking Confirmation` option is turned off then the
   * created appt is automaticaly confirmed and booked, so the event text won't contain 'HOLD'.
   * @param hostUserDisplayName String containing the host account's user display name
   * @param requsterName String containing the name of the requester (provided at booking request)
   * @param slotDate String containing date of the requested slot (format e.g: 'February 7, 2025')
   * @param slotTime String containg the time of the requested slot (format e.g: '03:30 PM')
   * @param confirmBooking Boolean whether the requested appt booking requires confirmation
   */
  async verifyEventCreated(hostUserDisplayName: string, requsterName: string, slotDate: string, slotTime: string, confirmBooking: boolean = true) {
    // now wait a max of 2 minutes for the newly request appt to appear in the dashboard pending appts list
    await expect(async () => {
      // depending on environment switch to the bookings page and verify the appt was created
      if (confirmBooking) {
        await this.gotoPendingBookings();
      } else {
        await this.gotoBookedBookings();
      }

      await this.page.waitForTimeout(TIMEOUT_3_SECONDS);
      const apptLocator = this.page.getByRole('row', { name: `Open appointment in new tab ${slotDate} ${slotTime} to` }).getByLabel('Open appointment in new tab')
      await apptLocator.scrollIntoViewIfNeeded();
      await expect(apptLocator).toBeVisible();
    }).toPass({
      // Probe, wait 1s, probe, wait 2s, probe, wait 10s, probe, wait 10s, probe
      // ... Defaults to [100, 250, 500, 1000].
      intervals: [15_000, 10_000, 5_000],
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
