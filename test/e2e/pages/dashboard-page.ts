import { expect, type Page, type Locator } from '@playwright/test';

import {
  APPT_PENDING_BOOKINGS_PAGE,
  APPT_BOOKED_BOOKINGS_PAGE,
  APPT_DASHBOARD_MONTH_PAGE,
  TIMEOUT_1_SECOND,
  TIMEOUT_3_SECONDS,
  TIMEOUT_60_SECONDS,
  TIMEOUT_30_SECONDS,
} from '../const/constants';


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
  readonly availabilityPanelHeader: Locator;
  readonly firstDayOfWeekMonthView: Locator;
  readonly setAvailabilityText: Locator;
  readonly customizePerDayCheckBox: Locator;
  readonly allStartTimeInput: Locator;
  readonly allEndTimeInput: Locator;
  readonly customStartTime1Input: Locator;
  readonly customStartTime2Input: Locator;
  readonly customStartTime3Input: Locator;
  readonly customStartTime4Input: Locator;
  readonly customStartTime5Input: Locator;
  readonly editLinkBtn: Locator;
  readonly saveChangesBtn: Locator;
  readonly revertChangesBtn: Locator;

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
    this.availabilityPanelHeader = this.page.getByPlaceholder('My Schedule');
    this.firstDayOfWeekMonthView = this.page.locator('.calendar-month__week-day-name').first();
    this.setAvailabilityText = this.page.getByText('Set your availability days and time');
    this.customizePerDayCheckBox = this.page.getByRole('checkbox', { name: 'Customize per day'});
    this.allStartTimeInput = this.page.locator('#start_time');
    this.allEndTimeInput = this.page.locator('#end_time');
    this.customStartTime1Input = this.page.getByTestId('dashboard-availability-start-time-1-0-input');
    this.customStartTime2Input = this.page.getByTestId('dashboard-availability-start-time-2-0-input');
    this.customStartTime3Input = this.page.getByTestId('dashboard-availability-start-time-3-0-input');
    this.customStartTime4Input = this.page.getByTestId('dashboard-availability-start-time-4-0-input');
    this.customStartTime5Input = this.page.getByTestId('dashboard-availability-start-time-5-0-input');
    this.editLinkBtn = this.page.getByTestId('dashboard-availability-edit-link-btn');
    this.saveChangesBtn = this.page.getByTestId('dashboard-save-changes-btn');
    this.revertChangesBtn = this.page.getByRole('button', { name: 'Revert changes' });
  }

  /**
   * Navigate to the pending bookings page and display all future pending bookings
   */
  async gotoPendingBookings() {
    await this.page.goto(APPT_PENDING_BOOKINGS_PAGE);
    // ensure all future pending bookings are displayed
    await this.pendingBookingsFilterSelect.selectOption(this.allFutureBookingsOptionText, { timeout: TIMEOUT_60_SECONDS });
  }

  /**
   * Navigate to the booked bookings page and display all confirmed/booked bookings
   */
  async gotoBookedBookings() {
    await this.page.goto(APPT_BOOKED_BOOKINGS_PAGE);
    // ensure all future booked bookings are displayed
    await this.pendingBookingsFilterSelect.selectOption(this.allFutureBookingsOptionText, { timeout: TIMEOUT_60_SECONDS });
  }

  /**
   * With pending bookings list displayed, enter a filter string to narrow down the list
   */
  async filterPendingBookings(filterString: string) {
    await expect(this.apptsFilterInput).toBeVisible({ timeout: TIMEOUT_30_SECONDS});
    await this.apptsFilterInput.fill(filterString);
    await this.page.waitForTimeout(TIMEOUT_3_SECONDS);
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
        var eventFilter = `HOLD: Appointment - ${hostUserDisplayName} and ${requsterName}`;
      } else {
        await this.gotoBookedBookings();
        var eventFilter = `Appointment - ${hostUserDisplayName} and ${requsterName}`;
      }

      await this.filterPendingBookings(eventFilter);
      await this.page.waitForTimeout(TIMEOUT_3_SECONDS);
      await this.page.evaluate(() => window.scrollBy(0, document.body.scrollHeight));

      const apptLocator = this.page.getByRole('cell', { name: `${slotDate}` }).locator('div', { hasText: `${slotTime} to`});
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

  /**
   * Get the availability panel header text (i.e. '<display name>'s Availability')
   */
  async getAvailabilityPanelHeader(): Promise<string> {
    return await this.availabilityPanelHeader.inputValue({ timeout: TIMEOUT_60_SECONDS });
  }

  /**
   * Turn on the 'customize per day' availaiblity option and verify the daily time slots appear.
   */
  async turnOnCustomizePerDayAndVerify() {
    await this.customizePerDayCheckBox.scrollIntoViewIfNeeded(); 
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    await this.customizePerDayCheckBox.check();
    await this.page.waitForTimeout(TIMEOUT_3_SECONDS);
    await expect(this.customStartTime1Input).toBeVisible();
    await expect(this.customStartTime1Input).toBeEnabled();
    await expect(this.customStartTime2Input).toBeVisible();
    await expect(this.customStartTime2Input).toBeEnabled();
    await expect(this.customStartTime3Input).toBeVisible();
    await expect(this.customStartTime3Input).toBeEnabled();
    await expect(this.customStartTime4Input).toBeVisible();
    await expect(this.customStartTime4Input).toBeEnabled();
    await expect(this.customStartTime5Input).toBeVisible();
    await this.customStartTime5Input.scrollIntoViewIfNeeded();
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    await expect(this.customStartTime5Input).toBeEnabled();
  }

  /**
   * Turn off the 'customize per day' availaiblity option and verify the daily time slots are gone.
   */
  async turnOffCustomizePerDayAndVerify() {
    await this.customizePerDayCheckBox.scrollIntoViewIfNeeded();
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    await this.customizePerDayCheckBox.uncheck();
    await this.page.waitForTimeout(TIMEOUT_3_SECONDS);
    await expect(this.customStartTime1Input).toBeHidden();
    await expect(this.customStartTime2Input).toBeHidden();
    await expect(this.customStartTime3Input).toBeHidden();
    await expect(this.customStartTime4Input).toBeHidden();
    await expect(this.customStartTime5Input).toBeHidden();
  }
}
