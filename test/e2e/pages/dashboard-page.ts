import { expect, type Page, type Locator } from '@playwright/test';
import { APPT_TARGET_ENV, APPT_PENDING_BOOKINGS_PAGE, APPT_BOOKED_BOOKINGS_PAGE } from '../const/constants';


export class DashboardPage {
  readonly page: Page;
  readonly navBarDashboardBtn: Locator;
  readonly userMenuAvatar: Locator;
  readonly logOutMenuItem: Locator;
  readonly shareMyLink: Locator;
  readonly nextMonthArrow: Locator;
  readonly pendingBookingsPageHeader: Locator;
  readonly pendingBookingsFilterSelect: Locator;
  readonly allFutureBookingsOptionText: string = 'All future bookings';
  readonly apptsFilterInput: Locator;

  constructor(page: Page) {
    this.page = page;
    this.navBarDashboardBtn = this.page.getByRole('link', { name: 'Dashboard' });
    this.userMenuAvatar = this.page.getByTestId('user-menu-avatar');
    this.logOutMenuItem = this.page.getByTestId('user-nav-logout-menu');
    this.shareMyLink = this.page.getByTestId('dashboard-share-quick-link-btn');
    this.nextMonthArrow = this.page.locator('[data-icon="chevron-right"]');
    this.pendingBookingsPageHeader = this.page.getByText('Bookings');
    this.pendingBookingsFilterSelect = this.page.getByTestId('bookings-filter-select');
    this.apptsFilterInput = this.page.getByPlaceholder('Search bookings');
  }

  /**
   * Navigate to the pending bookings page and display all future pending bookings
   */
  async gotoPendingBookings() {
    await this.page.goto(APPT_PENDING_BOOKINGS_PAGE);
    await this.page.waitForLoadState('domcontentloaded');
    // ensure all future pending bookings are displayed
    await this.pendingBookingsFilterSelect.selectOption(this.allFutureBookingsOptionText, { timeout: 60_000 });
  }

  /**
   * Navigate to the booked bookings page and display all confirmed/booked bookings
   */
  async gotoBookedBookings() {
    await this.page.goto(APPT_BOOKED_BOOKINGS_PAGE);
    await this.page.waitForLoadState('domcontentloaded');
    // ensure all future booked bookings are displayed
    await this.pendingBookingsFilterSelect.selectOption(this.allFutureBookingsOptionText, { timeout: 60_000 });
  }

  /**
   * With pending bookings list displayed, enter a filter string to narrow down the list
   */
  async filterPendingBookings(filterString: string) {
    await this.apptsFilterInput.fill(filterString);
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
    // depending on environment switch to the bookings page and verify the appt was created
    if (confirmBooking) {
      await this.gotoPendingBookings();
      var eventFilter = `HOLD: Appointment - ${hostUserDisplayName} and ${requsterName}`;
    } else {
      await this.gotoBookedBookings();
      var eventFilter = `Appointment - ${hostUserDisplayName} and ${requsterName}`;
    }
    await this.filterPendingBookings(eventFilter);

    // now we have a list of future pending appointments for our host and requster; now ensure one
    // of them matches the slot that was selected by the test
    const apptLocator = this.page.getByRole('cell', { name: `${slotDate}` }).locator('div', { hasText: `${slotTime} to`});
    await expect(apptLocator).toBeVisible( { timeout: 60_000 });
  }
}
