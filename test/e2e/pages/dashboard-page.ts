import { expect, type Page, type Locator } from '@playwright/test';

export class DashboardPage {
  readonly page: Page;
  readonly navBarDashboardBtn: Locator;
  readonly userMenuAvatar: Locator;
  readonly logOutMenuItem: Locator;
  readonly shareMyLink: Locator;
  readonly nextMonthArrow: Locator;

  constructor(page: Page) {
    this.page = page;
    this.navBarDashboardBtn = this.page.getByRole('link', { name: 'Dashboard' });
    this.userMenuAvatar = this.page.getByTestId('user-menu-avatar');
    this.logOutMenuItem = this.page.getByTestId('user-nav-logout-menu');
    this.shareMyLink = this.page.getByTestId('dashboard-share-quick-link-btn');
    this.nextMonthArrow = this.page.locator('[data-icon="chevron-right"]');
  }

  /**
   * With the booking page week view already displayed, go forward to the next week.
   */
  async goForwardOneMonth() {
    console.log('skipping ahead to the next calendar month');
    await this.nextMonthArrow.click();
    await this.page.waitForLoadState('domcontentloaded');
    await expect(this.shareMyLink).toBeVisible({ timeout: 30_000 });
  }

  /**
   * Given a requested booking's time slot reference, verify that a corresponding hold event
   * was created in the host calendar dashboard month view.
   * @param requestedBookingTimeSlotRef String containing the requested booking time slot ref
   * taken from the DOM on the share link page at the time when the slot was chosen. Will be in
   * the format of: 'event-2025-01-14 14:30'.
   * @param hostUserDisplayName String containing the host account's user display name
   * @param requsterName String containing the name of the requester (provided at booking request)
   */
  async verifyHoldEventCreated(requestedBookingTimeSlotRef: string, hostUserDisplayName: string, requsterName: string) {
    // on the host calendar view, hold appointment dom elements contain ids that look like this:
    // 'calendar-month__event-HOLD: Appointment - tbautomation1 and Automated-Test-Bot2025-01-09'
    // in this case 'tbautomation1' is the appointment host user who shares the booking link; and
    // `Automated-Test-Bot` is the booking requester's name. First build a search string to match.
    const eventDate = requestedBookingTimeSlotRef.substring(6, 16); // i.e. '2025-01-14'
    const eventSearchId = `calendar-month__event-HOLD: Appointment - ${hostUserDisplayName} and ${requsterName}${eventDate}`;
    console.log(`searching for calendar event with dom element id: ${eventSearchId}`);

    // todo: the hold event dom element id only contains the event date and not time slot so if we
    // search we will get all events on that date for the given users but won't be able to tell if
    // hold event was created for the correct time slot; for now just ensure at lest one hold event
    // was created on the booking request date, but update this later (see github issue #820).

    // check if the hold event is found on current month view
    const holdEvent: Locator = this.page.locator(`id=${eventSearchId}`);
    const firstHoldEvent: Locator = holdEvent.first();
    var eventText = await firstHoldEvent.innerText();
    if (!eventText) {
      // hold event not found in current month view so skip ahead to the next month and check again
      console.log('no matching hold event found in current month');
      await this.goForwardOneMonth();
      eventText = await firstHoldEvent.innerText();
      expect(eventText.length, 'matching hold event was not found on host calendar!').toBeGreaterThan(4);
    }

    // at least one matching hold event found
    console.log(`matching hold event found, has text: ${eventText}`);
    const expHoldEventText = `HOLD: Appointment - ${hostUserDisplayName} and ${requsterName}`;
    expect(eventText).toContain(expHoldEventText);
  }
}
