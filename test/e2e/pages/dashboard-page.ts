import { expect, type Page, type Locator } from '@playwright/test';
import { format } from 'date-fns';

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
   * in the host account's list of bookings.
   * @param selectedSlot String containing date time of the requested slot (format 'event-2026-01-23 17:00')
   * as provided from the bookee page (dom element of the requested time slot)
   */
  async verifyEventCreated(selectedSlot: string) {
    // now wait a max of 2 minutes for the newly request appt to appear in the dashboard pending appts list
    await expect(async () => {
      await this.gotoBookings();
      await this.page.waitForTimeout(TIMEOUT_3_SECONDS);

      // the selected slot date and time is received in the format 'event-2026-01-23 17:00', but on the bookings
      // page list bookings are listed in the format of '01/23/2026, 5:00 PM'; so convert received string to match
      const selectedSlotStr = selectedSlot.substring(6).replace(' ', 'T'); // '2026-01-23T17:00'
      const selectedSlotDateObj = new Date(selectedSlotStr);
      const selectedSlotFormattedDate = format(selectedSlotDateObj, 'MM/dd/yyyy, h:mm a'); // '01/23/2026, 5:00 PM'

      // now our selected slot is in the same format we can seach for it on the pending bookings list
      console.log(`searching bookings list for event: ${selectedSlotFormattedDate}`);
      const apptLocator = this.page.getByRole('button', { name: selectedSlotFormattedDate });
      await apptLocator.scrollIntoViewIfNeeded();
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
