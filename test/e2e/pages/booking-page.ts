import { expect } from '@playwright/test';
import { type Page, type Locator } from '@playwright/test';
import { APPT_MY_SHARE_LINK, APPT_SHORT_SHARE_LINK_PREFIX, APPT_LONG_SHARE_LINK_PREFIX, TIMEOUT_30_SECONDS, APPT_TIMEZONE_SETTING_PRIMARY, TIMEOUT_2_SECONDS } from '../const/constants';

export class BookingPage {
  readonly page: Page;
  readonly testPlatform: String;
  readonly titleText: Locator;
  readonly bookingPageTimeZoneFooter: Locator;
  readonly bookATimeToMeetText: Locator;
  readonly selectTimeSlotText: Locator;
  readonly bookApptBtn: Locator;
  readonly bookingCalendarHdrSun: Locator;
  readonly bookingCalendarHdrMon: Locator;
  readonly bookingCalendarHdrTue: Locator;
  readonly bookingCalendarHdrWed: Locator;
  readonly bookingCalendarHdrThu: Locator;
  readonly bookingCalendarHdrFri: Locator;
  readonly bookingCalendarHdrSat: Locator;
  readonly bookingWeekPickerBtn: Locator;
  readonly nextWeekArrow: Locator;
  readonly availableBookingSlot: Locator;
  readonly bookSelectionNameInput: Locator;
  readonly bookSelectionEmailInput: Locator;
  readonly bookingRequestedTitleText: Locator;
  readonly requestSentAvailabilityText: Locator;
  readonly requestSentCloseBtn: Locator;
  readonly eventBookedTitleText: Locator;
  readonly scheduleTurnedOffText: Locator;
  readonly bookApptPage7AMSlot: Locator;
  readonly bookApptPage630PMSlot: Locator;
  readonly bookApptPage15MinSlot: Locator;

  constructor(page: Page, testPlatform: string = 'desktop') {
    this.page = page;
    this.testPlatform = testPlatform;
    this.titleText = this.page.getByTestId('booking-view-title-text');
    this.bookingPageTimeZoneFooter = this.page.locator('div').filter({ hasText: /^Timezone:/ });
    this.bookATimeToMeetText = this.page.getByTestId('booking-view-book-a-time-to-meet-with-text');
    this.selectTimeSlotText = this.page.getByText('Select an open time slot from the calendar');
    this.bookingCalendarHdrSun = this.page.getByText('SUN', { exact: true });
    this.bookingCalendarHdrMon = this.page.getByText('MON', { exact: true });
    this.bookingCalendarHdrTue = this.page.getByText('TUE', { exact: true });
    this.bookingCalendarHdrWed = this.page.getByText('WED', { exact: true });
    this.bookingCalendarHdrThu = this.page.getByText('THU', { exact: true });
    this.bookingCalendarHdrFri = this.page.getByText('FRI', { exact: true });
    this.bookingCalendarHdrSat = this.page.getByText('SAT', { exact: true });
    this.bookingWeekPickerBtn = this.page.locator('.week-picker-button');
    this.nextWeekArrow = this.page.getByRole('button', { name: 'Next week' });
    this.availableBookingSlot = this.page.locator('.selectable-slot', { hasNotText: 'Busy' });
    this.bookSelectionNameInput = this.page.locator('[name="booker-view-user-name"]');
    this.bookSelectionEmailInput = this.page.locator('[name="booker-view-user-email"]');
    this.bookApptBtn = this.page.getByTestId('booking-view-confirm-selection-button');
    this.bookingRequestedTitleText = this.page.getByText('Booking Request Sent');
    this.requestSentAvailabilityText = this.page.getByText("'s Availability");
    this.requestSentCloseBtn = this.page.getByRole('button', { name: 'Close' });
    this.eventBookedTitleText = this.page.getByText('Event booked!');
    this.scheduleTurnedOffText = this.page.getByText('The schedule has been turned off.');
    this.bookApptPage7AMSlot = this.page.getByText('7:00 AM', { exact: true }).first();
    this.bookApptPage630PMSlot = this.page.getByText(':30 PM').first();
    this.bookApptPage15MinSlot = this.page.getByText(':15 AM').first();
  }

  /**
   * Navigate to the booking page using the share link short URL.
   */
  async gotoBookingPageShortUrl() {
    // the default share link is a short URL
    await this.page.goto(APPT_MY_SHARE_LINK);
    await expect(this.selectTimeSlotText).toBeVisible( { timeout: TIMEOUT_30_SECONDS });
  }

  /**
   * Navigatge to the booking page using the share link long URL.
   */
  async gotoBookingPageLongUrl() {
    // the share link is short by default; build the corresponding long link first
    const prodShareLinkUser: string = APPT_MY_SHARE_LINK.split(APPT_SHORT_SHARE_LINK_PREFIX)[1];
    const longLink: string = `${APPT_LONG_SHARE_LINK_PREFIX}${prodShareLinkUser}`;
    await this.page.goto(longLink);
    await expect(this.selectTimeSlotText).toBeVisible( { timeout: TIMEOUT_30_SECONDS });
  }

  /**
   * Go to the booking page week view (via the booking share link)
   */
  async gotoBookingPageWeekView() {
    const weekLink: string = `${APPT_MY_SHARE_LINK}#week`;
    await this.page.goto(weekLink);
    await expect(this.selectTimeSlotText).toBeVisible( { timeout: TIMEOUT_30_SECONDS });
  }

  /**
   * With the booking page week view already displayed, go forward to the next week.
   */
  async goForwardOneWeek() {
    await this.nextWeekArrow.click();
    await expect(this.selectTimeSlotText).toBeVisible( { timeout: TIMEOUT_30_SECONDS });
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
    // playwrignt doesn't yet support 'count' or 'all' or 'elementHandles' on ios
    var availableSlot: Locator = this.availableBookingSlot.first();

    // if no slots are available in current week view then fast forward to next week
    if (!availableSlot) {
      console.log('no slots available in current week, skipping ahead to the next week');
      await this.goForwardOneWeek();
      // now check again for available slots; if none then fail out the test (safety catch but shouldn't happen)
      availableSlot = this.availableBookingSlot.first();
      expect(availableSlot, `no booking slots available, please check availability settings for ${userDisplayName}`).toBeTruthy();
    }

    // get our slot info for the available slot that we are going to request
    let slotRef = await availableSlot.getAttribute('data-testid'); // ie. 'event-2025-01-08 09:30'
    if (!slotRef)
      slotRef = 'none';
    expect(slotRef).toContain('event-');

    // now that we've found an availalbe slot select it and confirm
    await availableSlot.click();
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

    // when clicking the book appt button for some reason on android it won't click it unless we force it; but
    // force doesn't work on ios
    if (this.testPlatform.includes('android')) { 
      await this.bookApptBtn.click({ force: true });
    } else {
      await this.bookApptBtn.click();
    }
    // slight delay so on mobile we can see if any errors show up in BrowserStack test playback videos
    await this.page.waitForTimeout(TIMEOUT_2_SECONDS);
  }

  /**
   * Utility to return a string containing the date abstracted from a given time slot string 
   * @param timeSlotString Slot string read from DOM (ie. 'event-2025-01-14 14:30')
   * @returns Formatted date string month and day only (ie. 'Jan 14')
   */
  async getDateFromSlotString(timeSlotString: string): Promise<string> {
    const selectedSlotDateTime = new Date(timeSlotString.substring(6));

    const options:Intl.DateTimeFormatOptions = {
      month: "short",
      day: "numeric",
    };

    return selectedSlotDateTime.toLocaleDateString('default', options);
  }

  /**
   * Utility to return a string containing the event start time abstracted from a
   * given time slot string.
   * @param timeSlotString Slot string read from DOM (ie. 'event-2025-01-14 14:30')
   * @returns Formatted event start time string (ie. '02:30pm')
   */
  async getStartTimeFromSlotString(timeSlotString: string): Promise<string> {
    const selectedSlotDateTime = new Date(timeSlotString.substring(6));
    var startTimeStr = selectedSlotDateTime.toLocaleTimeString('default', { hour12: true, hour: '2-digit', minute: '2-digit' });
    // now startTimeStr looks like this, for example: '04:30 p.m.' but need it to be like '04:30pm'
    startTimeStr = startTimeStr.replace(' ', '').replace('.', '').replace('.', '');
    return startTimeStr
  }

  /**
   * Scroll the given element into view. The reason why we do this here is because playright doesn't yet supported this on ios.
   */
  async scrollIntoView(targetElement: Locator, timeout: number = 10000) {
    if (!this.testPlatform.includes('ios')) {
      await targetElement.scrollIntoViewIfNeeded({ timeout: timeout });
    }
  }
}
