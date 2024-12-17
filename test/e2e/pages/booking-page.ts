import { type Page, type Locator } from '@playwright/test';

export class BookingPage {
  readonly page: Page;
  readonly titleText: Locator;
  readonly invitingText: Locator;

  constructor(page: Page) {
    this.page = page;
    this.titleText = page.getByTestId('booking-view-title-text');
    this.invitingText = page.getByTestId('booking-view-inviting-you-text');
  }

  async gotoBookingPage(bookingPageURL: string) {
    await this.page.goto(bookingPageURL);
    await this.page.waitForLoadState('domcontentloaded');
  }
}
