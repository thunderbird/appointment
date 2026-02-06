import { expect, type Page, type Locator } from '@playwright/test';

import {
  APPT_AVAILABILITY_PAGE,
  APPT_TIMEZONE_SETTING_PRIMARY,
  TIMEOUT_1_SECOND,
  TIMEOUT_3_SECONDS,
  TIMEOUT_10_SECONDS,
  TIMEOUT_30_SECONDS,
} from '../const/constants';


export class AvailabilityPage {
  readonly page: Page;
  readonly saveChangesBtn: Locator;
  readonly savedSuccessfullyText: Locator;
  readonly revertChangesBtn: Locator;
  readonly setAvailabilityText: Locator;
  readonly bookableToggle: Locator;
  readonly bookableToggleContainer: Locator;
  readonly timeZoneSelect: Locator;
  readonly calendarSelect: Locator;
  readonly autoConfirmBookingsCheckBox: Locator;
  readonly customizePerDayCheckBox: Locator;
  readonly customizePerDayCheckBoxContainer: Locator;
  readonly allStartTimeInput: Locator;
  readonly allEndTimeInput: Locator;
  readonly customStartTime1Input: Locator;
  readonly customStartTime2Input: Locator;
  readonly customStartTime3Input: Locator;
  readonly customStartTime4Input: Locator;
  readonly customStartTime5Input: Locator;
  readonly minNoticeInput: Locator;
  readonly bookingWindowInput: Locator;
  readonly bookingPageDetailsHdr: Locator;
  readonly bookingPageNameInput: Locator;
  readonly bookingPageDescInput: Locator;
  readonly bookingPageMtgLinkInput: Locator;
  readonly bookingPageMtgDur15MinBtn: Locator;
  readonly bookingPageMtgDur30MinBtn: Locator;
  readonly bookingPageLinkHdr: Locator;
  readonly refreshLinkBtn: Locator;
  readonly refreshLinkConfirmTxt: Locator;
  readonly refreshLinkConfirmCancelBtn: Locator;
  readonly shareYourLinkInput: Locator;
  readonly shareLinkCopyBtn: Locator;

  constructor(page: Page) {
    this.page = page;
    this.saveChangesBtn = this.page.getByTestId('notice-bar').getByRole('button', { name: 'Save changes' });
    this.savedSuccessfullyText = this.page.getByText('Availability saved successfully', { exact: true });
    this.revertChangesBtn = this.page.getByTestId('notice-bar').getByRole('button', { name: 'Revert changes' });

    // set your availability section
    this.setAvailabilityText = this.page.getByText('Set Your Availability');
    this.bookableToggle = this.page.getByTestId('availability-set-availability-toggle');
    this.bookableToggleContainer = this.page.getByTitle('Activate schedule');
    this.timeZoneSelect = this.page.getByLabel(APPT_TIMEZONE_SETTING_PRIMARY);
    this.calendarSelect = this.page.locator('select[name="calendar"]');
    this.autoConfirmBookingsCheckBox = this.page.getByTestId('availability-automatically-confirm-checkbox');
    this.customizePerDayCheckBox = this.page.getByRole('checkbox', { name: 'Set custom times for each day'});
    this.customizePerDayCheckBoxContainer = this.page.locator('label').filter({ hasText: 'Set custom times for each day' }).locator('span').first();

    this.allStartTimeInput = this.page.locator('#start_time');
    this.allEndTimeInput = this.page.locator('#end_time');
    this.customStartTime1Input = this.page.getByTestId('availability-start-time-1-0-input');
    this.customStartTime2Input = this.page.getByTestId('availability-start-time-2-0-input');
    this.customStartTime3Input = this.page.getByTestId('availability-start-time-3-0-input');
    this.customStartTime4Input = this.page.getByTestId('availability-start-time-4-0-input');
    this.customStartTime5Input = this.page.getByTestId('availability-start-time-5-0-input');
    this.minNoticeInput = this.page.getByRole('button', { name: 'instant' });
    this.bookingWindowInput = this.page.getByRole('button', { name: '7 days' });

    // booking page details section
    this.bookingPageDetailsHdr = this.page.getByRole('heading', { name: 'Booking Page Details' });
    this.bookingPageNameInput = this.page.locator('#pageName');
    this.bookingPageDescInput = this.page.locator('#pageDescription');
    this.bookingPageMtgLinkInput = this.page.locator('#virtualMeetingLink');
    this.bookingPageMtgDur15MinBtn = this.page.getByText('15 Min');
    this.bookingPageMtgDur30MinBtn = this.page.getByRole('button', { name: '30 Min' });

    // booking page link section
    this.bookingPageLinkHdr = this.page.getByRole('heading', { name: 'Your Booking Page Link' });
    this.refreshLinkBtn = this.page.getByRole('button', { name: 'Refresh link' });
    this.refreshLinkConfirmTxt = this.page.getByText('Refresh link', { exact: true });
    this.refreshLinkConfirmCancelBtn = this.page.getByRole('button', { name: 'Cancel' });
    this.shareYourLinkInput = this.page.locator('#bookingPageLinkInput');
    this.shareLinkCopyBtn = this.page.getByRole('button', { name: 'Copy', exact: true });
  }

  /**
   * Navigate to the availability page
   */
  async gotoAvailabilityPage() {
    // go to availability page, sometimes takes a bit to load all element values!
    await this.page.goto(APPT_AVAILABILITY_PAGE, { timeout: TIMEOUT_30_SECONDS });
    await this.page.waitForTimeout(TIMEOUT_10_SECONDS);
    await this.bookableToggleContainer.waitFor({ timeout: TIMEOUT_30_SECONDS });
    await this.allStartTimeInput.waitFor({ timeout: TIMEOUT_30_SECONDS });
    await this.bookingPageMtgDur15MinBtn.waitFor({ timeout: TIMEOUT_30_SECONDS });
    await this.minNoticeInput.waitFor({ timeout: TIMEOUT_30_SECONDS });
  }

  /**
   * Turn on the 'customize per day' availaiblity option and verify the daily time slots appear.
   */
  async turnOnCustomizePerDayAndVerify() {
    await this.customizePerDayCheckBox.scrollIntoViewIfNeeded(); 
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    if (!await this.customizePerDayCheckBox.isChecked()) {
      // container blocks cbox itself so click container to change
      await this.customizePerDayCheckBoxContainer.click();
      await this.page.waitForTimeout(TIMEOUT_3_SECONDS);
      await expect(this.customStartTime1Input).toBeVisible();
      expect(await this.customStartTime1Input.isVisible()).toBeTruthy();
      await expect(this.customStartTime1Input).toBeEnabled();
      expect(await this.customStartTime2Input.isVisible()).toBeTruthy();
      await expect(this.customStartTime2Input).toBeEnabled();
      expect(await this.customStartTime3Input.isVisible()).toBeTruthy();
      await expect(this.customStartTime3Input).toBeEnabled();
      expect(await this.customStartTime4Input.isVisible()).toBeTruthy();
      await expect(this.customStartTime4Input).toBeEnabled();
      expect(await this.customStartTime5Input.isVisible()).toBeTruthy();
      await this.customStartTime5Input.scrollIntoViewIfNeeded();
      await this.page.waitForTimeout(TIMEOUT_1_SECOND);
      await expect(this.customStartTime5Input).toBeEnabled();
    }
  }

  /**
   * Turn off the 'customize per day' availaiblity option and verify the daily time slots are gone.
   */
  async turnOffCustomizePerDayAndVerify() {
    await this.customizePerDayCheckBox.scrollIntoViewIfNeeded();
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    if (await this.customizePerDayCheckBox.isChecked()) {
      // container blocks cbox itself so click container to change
      await this.customizePerDayCheckBoxContainer.click();
      await this.page.waitForTimeout(TIMEOUT_3_SECONDS);
      expect(await this.customStartTime1Input.isVisible()).toBeFalsy();
      expect(await this.customStartTime2Input.isVisible()).toBeFalsy();
      expect(await this.customStartTime3Input.isVisible()).toBeFalsy();
      expect(await this.customStartTime4Input.isVisible()).toBeFalsy();
      expect(await this.customStartTime5Input.isVisible()).toBeFalsy();
    }
  }
}
