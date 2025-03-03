import { expect } from '@playwright/test';
import { type Page, type Locator } from '@playwright/test';
import { APPT_MY_SHARE_LINK, APPT_SHORT_SHARE_LINK_PREFIX, APPT_LONG_SHARE_LINK_PREFIX, TIMEOUT_30_SECONDS } from '../const/constants';

export class BookingPage {
  readonly page: Page;
  readonly titleText: Locator;
  readonly invitingText: Locator;
  readonly confirmBtn: Locator;
  readonly bookingCalendar: Locator;
  readonly calendarHeader: Locator;
  readonly nextMonthArrow: Locator;
  readonly availableBookingSlot: Locator;
  readonly bookSelectionNameInput: Locator;
  readonly bookSelectionEmailInput: Locator;
  readonly bookSelectionBookBtn: Locator;
  readonly requestSentTitleText: Locator;
  readonly requestSentAvailabilityText: Locator;
  readonly requestSentCloseBtn: Locator;
  readonly eventBookedTitleText: Locator;

  constructor(page: Page) {
    this.page = page;
    this.titleText = this.page.getByTestId('booking-view-title-text');
    this.invitingText = this.page.getByTestId('booking-view-inviting-you-text');
    this.bookingCalendar = this.page.getByTestId('booking-view-calendar-div');
    this.confirmBtn = this.page.getByTestId('booking-view-confirm-selection-button');
    this.calendarHeader = this.page.locator('.calendar-header__period-name');
    this.nextMonthArrow = this.page.locator('[data-icon="chevron-right"]');
    this.availableBookingSlot = this.page.locator('[data-test="day-event"]', { hasNotText: 'Busy'});
    this.bookSelectionNameInput = this.page.getByPlaceholder('First and last name');
    this.bookSelectionEmailInput = this.page.getByPlaceholder('john.doe@example.com');
    this.bookSelectionBookBtn = this.page.getByRole('button', { name: 'Book' });
    this.requestSentTitleText = this.page.getByText('Booking request sent');
    this.requestSentAvailabilityText = this.page.getByText("'s Availability");
    this.requestSentCloseBtn = this.page.getByRole('button', { name: 'Close' });
    this.eventBookedTitleText = this.page.getByText('Event booked!');
  }

  /**
   * Navigate to the booking page using the share link short URL.
   */
  async gotoBookingPageShortUrl() {
    // the default share link is a short URL
    await this.page.goto(APPT_MY_SHARE_LINK);
  }

  /**
   * Navigatge to the booking page using the share link long URL.
   */
  async gotoBookingPageLongUrl() {
    // the share link is short by default; build the corresponding long link first
    const prodShareLinkUser: string = APPT_MY_SHARE_LINK.split(APPT_SHORT_SHARE_LINK_PREFIX)[1];
    const longLink: string = `${APPT_LONG_SHARE_LINK_PREFIX}${prodShareLinkUser}`;
    await this.page.goto(longLink);
  }

  /**
   * Go to the booking page week view (via the booking share link)
   */
  async gotoBookingPageWeekView() {
    const weekLink: string = `${APPT_MY_SHARE_LINK}#week`;
    await this.page.goto(weekLink);
    await expect(this.confirmBtn).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
  }

  /**
   * With the booking page week view already displayed, go forward to the next week.
   */
  async goForwardOneWeek() {
    await this.nextMonthArrow.click();
    await expect(this.confirmBtn).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
  }

  /**
   * With the booking page week view already displayed, select the first available booking slot.
   * If there is no slot available on the current week, this methond will skip to the next week
   * and look for slots there. If no slots are avaible on the next week either, then an error
   * will be raised.
   * @param userDisplayName String containing the display name of the Appointment user
   * @returns String containing the reference text for the time slot that was requested
   * as retrieved from the DOM ie. 'event-2025-01-08 09:30'.
   */
  async selectAvailableBookingSlot(userDisplayName: string): Promise<string> {
    // let's check if a non-busy appointment slot exists in the current week view
    const slotCount: number = await this.availableBookingSlot.count();
    console.log(`available slot count: ${slotCount}`);

    // if no slots are available in current week view then fast forward to next week
    if (slotCount === 0) {
      console.log('no slots available in current week, skipping ahead to the next week');
      await this.goForwardOneWeek();
      // now check again for available slots; if none then fail out the test (safety catch but shouldn't happen)
      const newSlotCount: number = await this.availableBookingSlot.count();
      console.log(`available slot count: ${newSlotCount}`);
      expect(newSlotCount, `no booking slots available, please check availability settings for ${userDisplayName}`).toBeGreaterThan(0);
    }

    // slots are available in current week view so get the first one
    const firstSlot: Locator = this.availableBookingSlot.first();
    let slotRef = await firstSlot.getAttribute('data-ref'); // ie. 'event-2025-01-08 09:30'
    if (!slotRef)
      slotRef = 'none';
    expect(slotRef).toContain('event-');

    // now that we've found an availalbe slot select it and confirm
    await firstSlot.click();
    return slotRef;
  }

  /**
   * Fill out the 'book selection' dialog with the given values.
   * The 'book selection' dialog appears after an appointment slot has been selected (on the
   * booking page provided by the share link). This method will fill in the booking requester's
   * name and email address and then click the 'book' button to finalize the booking request.
   * @param bookerName String to fill in as the booking requester's name
   * @param bookerEmail String to fill in as the booking requester's email
   */
  async finishBooking(bookerName: string, bookerEmail: string) {
    await this.bookSelectionNameInput.fill(bookerName);
    await this.bookSelectionEmailInput.fill(bookerEmail);
    await this.bookSelectionBookBtn.click();
  }

  /**
   * Verify the given appointment time slot text is displayed in the current page
   * @param expSlotDateStr Expected slot date string formatted as 'Friday, January 10, 2025'
   * @param expSlotTimeStr Expected time slot time string formatted as '14:30' (24 hr time)
   */
  async verifyRequestedSlotTextDisplayed(expSlotDateStr: string, expSlotTimeStr: string) {
    // due to the way the element is we must locate by the date text only
    const slotDisplayText: Locator = this.page.getByText(expSlotDateStr);
    await expect(slotDisplayText).toBeVisible();
    // the slot text has been found so now verify it contains both the given date and time
    await expect(slotDisplayText).toHaveText(`${expSlotDateStr} ${expSlotTimeStr}`);
  }

  /**
   * Utility to return a string containing the date abstracted from a given time slot string 
   * @param timeSlotString Slot string read from DOM (ie. 'event-2025-01-14 14:30')
   * @returns Formatted date string (ie. 'Tuesday, January 14, 2025')
   */
  async getDateFromSlotString(timeSlotString: string): Promise<string> {
    const selectedSlotDateTime = new Date(timeSlotString.substring(6));
    return selectedSlotDateTime.toLocaleDateString('default', { dateStyle: 'full' });
  }

  /**
   * Utility to return a string containg the time abstracted from a given time slot string.
   * The time in the given time slot string is in 24 hour format (i.e. 14:30), but we want
   * it to be like '02:30 PM'
   * @param timeSlotString Slot string read from DOM (ie. 'event-2025-01-14 14:30')
   * @returns Formatted time string (ie. '02:30 PM')
   */
  async getTimeFromSlotString(timeSlotString: string): Promise<string> {
    const selectedSlotDateTime = new Date(timeSlotString.substring(6));
    const expTimeStr = selectedSlotDateTime.toLocaleTimeString('default', { hour12: true, hour: '2-digit', minute: '2-digit' });
    // now expTimeStr looks like this, for example: '04:30 p.m.' but need it to be like '04:30 PM'
    return expTimeStr.toUpperCase().replace('.', '').replace('.', '');
  }
}
