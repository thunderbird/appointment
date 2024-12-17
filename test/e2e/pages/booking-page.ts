import { type Page, type Locator } from '@playwright/test';

export class BookingPage {
  readonly page: Page;
  readonly titleText: Locator;
  readonly invitingText: Locator;
  readonly confirmButton: Locator;
  readonly bookingCalendar: Locator;
  readonly calendarHeader: Locator;

  constructor(page: Page) {
    this.page = page;
    this.titleText = page.getByTestId('booking-view-title-text');
    this.invitingText = page.getByTestId('booking-view-inviting-you-text');
    this.bookingCalendar = page.getByTestId('booking-view-calendar-div');
    this.confirmButton = page.getByTestId('booking-view-confirm-selection-button');
    this.calendarHeader = page.locator('.calendar-header__period-name');
  }

  async gotoBookingPage(bookingPageURL: string) {
    await this.page.goto(bookingPageURL);
    await this.page.waitForLoadState('domcontentloaded');
  }
}
