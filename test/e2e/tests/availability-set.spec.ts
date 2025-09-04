import { test, expect } from '@playwright/test';
import { AvailabilityPage } from '../pages/availability-page';
import { BookingPage } from '../pages/booking-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  APPT_MY_SHARE_LINK,
  TIMEOUT_1_SECOND,
  TIMEOUT_3_SECONDS,
  TIMEOUT_60_SECONDS,
 } from '../const/constants';

let availabilityPage: AvailabilityPage;
let bookApptPage: BookingPage;

test.describe('set availability', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    // note: we are already signed into Appointment with our default settings (via our auth-setup)
    // availability panel is displayed open as default
    bookApptPage = new BookingPage(page);
    availabilityPage = new AvailabilityPage(page);
    await availabilityPage.gotoAvailabilityPage();
  });

  test('default availability settings are displayed', async ({ page }) => {
    // just verify that the default availability options are available/displayed
    // timzone display is covered in other tests so not checked here
    await expect(availabilityPage.setAvailabilityText).toBeVisible();

    // timezone displayed is correct
    await expect(availabilityPage.timeZoneText).toBeVisible();
    await availabilityPage.timeZoneText.scrollIntoViewIfNeeded();

    // selected calendar ('booking to') has value; takes a bit to load
    if ((await availabilityPage.calendarSelect.inputValue()).length == 0) {
      await page.waitForTimeout(TIMEOUT_3_SECONDS);
    }
    expect(await availabilityPage.calendarSelect.inputValue()).toBeTruthy();

    // automatically confirm bookings checkbox is on
    await availabilityPage.autoConfirmBookingsCheckBox.scrollIntoViewIfNeeded();
    await expect(availabilityPage.autoConfirmBookingsCheckBox).toBeChecked();

    // customize per day checkbox
    await availabilityPage.customizePerDayCheckBox.scrollIntoViewIfNeeded();
    await expect(availabilityPage.customizePerDayCheckBox).toBeVisible();
    await expect(availabilityPage.customizePerDayCheckBox).toBeEnabled();

    // if customize per day checkbox is NOT turned on then we will see overall start and end time inputs
    const customize_day = await availabilityPage.customizePerDayCheckBox.isChecked();
    if (!customize_day) {
      await expect(availabilityPage.allStartTimeInput).toBeVisible();
      await expect(availabilityPage.allStartTimeInput).toBeEnabled();
      await expect(availabilityPage.allEndTimeInput).toBeVisible();
      await expect(availabilityPage.allEndTimeInput).toBeEnabled();
    } else {
      await expect(availabilityPage.customStartTime1Input).toBeVisible();
      await expect(availabilityPage.customStartTime1Input).toBeEnabled();
      await expect(availabilityPage.customStartTime2Input).toBeVisible();
      await expect(availabilityPage.customStartTime2Input).toBeEnabled();
      await expect(availabilityPage.customStartTime3Input).toBeVisible();
      await expect(availabilityPage.customStartTime3Input).toBeEnabled();
      await expect(availabilityPage.customStartTime4Input).toBeVisible();
      await expect(availabilityPage.customStartTime4Input).toBeEnabled();
      await expect(availabilityPage.customStartTime5Input).toBeVisible();
      await expect(availabilityPage.customStartTime5Input).toBeEnabled();
    }

    // minimum notice is visible
    await availabilityPage.minNoticeInput.scrollIntoViewIfNeeded();
    await expect(availabilityPage.minNoticeInput).toBeVisible();

    // booking window is visible
    await availabilityPage.bookingWindowInput.scrollIntoViewIfNeeded();
    await expect(availabilityPage.bookingWindowInput).toBeVisible();

    // clicking time zone edit link navigates to settings page
    await availabilityPage.editTimeZoneBtn.scrollIntoViewIfNeeded();
    await availabilityPage.editTimeZoneBtn.click();
    await page.waitForURL('**/settings#preferences');
  });

  test('customize-per-day checkbox reveals daily time slots', async () => {
    // get current status of customize per day check box (so this test will run regardless of state)
    await expect(availabilityPage.customizePerDayCheckBox).toBeVisible({ timeout: TIMEOUT_60_SECONDS });
    await expect(availabilityPage.customizePerDayCheckBox).toBeEnabled({ timeout: TIMEOUT_60_SECONDS });

    const customize_per_day = await availabilityPage.customizePerDayCheckBox.isChecked();

    if (!customize_per_day) {
      // is off, turn it on, verify daily time slot options appear
      await availabilityPage.turnOnCustomizePerDayAndVerify();
      await availabilityPage.turnOffCustomizePerDayAndVerify();
    } else {
      // is on already, turn it off, verify daily time slot options aren't visible
      await availabilityPage.turnOffCustomizePerDayAndVerify();
      await availabilityPage.turnOnCustomizePerDayAndVerify();
    }
  });

  test('able to turn off availability', async ({ page }) => {
    // turn off availability (via the `you're bookable` toggle)
    // note: we can check the active/bookable toggle checkbox setting but playwright cannot
    // interact with it (i.e. click to turn off/on) because it is covered up by a component container;
    // in the ui you can see you can click on the text beside the toggle (ie. "You're bookable") and
    // that changes the setting
    await availabilityPage.bookableToggleContainer.scrollIntoViewIfNeeded();
    await expect(availabilityPage.bookableToggle).toBeChecked();
    await availabilityPage.bookableToggleContainer.click();
    await availabilityPage.saveChangesBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);

    // now that we've turned off availability we use expect.soft, that ensures the rest of the test will
    // run even if the assert fails, so that we ensure we turn availability back on again after; note that
    // the test will still be marked as a failure if an expect.soft assert fails, just it will finish first
    await expect.soft(availabilityPage.bookableToggle).toBeChecked({ checked: false });

    // go to share link/book appointment page and verify not available
    await page.goto(APPT_MY_SHARE_LINK);
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await expect.soft(bookApptPage.scheduleTurnedOffText).toBeVisible();

    // go back to availability page and turn back on availability toggle
    await availabilityPage.gotoAvailabilityPage();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await availabilityPage.bookableToggleContainer.scrollIntoViewIfNeeded();
    await expect.soft(availabilityPage.bookableToggle).toBeChecked({ checked: false });
    await availabilityPage.bookableToggleContainer.click();
    await availabilityPage.saveChangesBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await expect(availabilityPage.bookableToggle).toBeChecked();
  });

  test('able to change availability time', async ({ page }) => {
    // turn off 'automatically confirm bookings' checkbox and then revert
    await availabilityPage.autoConfirmBookingsCheckBox.scrollIntoViewIfNeeded();
    await expect(availabilityPage.autoConfirmBookingsCheckBox).toBeChecked();
    await availabilityPage.autoConfirmBookingsCheckBox.uncheck();
    await availabilityPage.revertChangesBtn.scrollIntoViewIfNeeded();
    await availabilityPage.revertChangesBtn.click();
    await expect(availabilityPage.autoConfirmBookingsCheckBox).toBeChecked();

    // change start time to 7:00 AM and end time 7:00 PM
    await availabilityPage.bookingWindowInput.scrollIntoViewIfNeeded(); // scroll to btm for debug screenshot
    await availabilityPage.allStartTimeInput.fill('07:00');
    await availabilityPage.allEndTimeInput.fill('19:00');
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await availabilityPage.saveChangesBtn.scrollIntoViewIfNeeded();
    await availabilityPage.saveChangesBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await expect(availabilityPage.savedSuccessfullyText).toBeVisible();

    // goto book appt page week view, ensure 7:00 AM and 6:30 PM appointment slot exists on any day
    // need the week view so that the entire day is displayed as checking earliest and latest slots
    await bookApptPage.gotoBookingPageWeekView();
    await expect(bookApptPage.bookApptPage7AMSlot).toBeVisible();
    await expect(bookApptPage.bookApptPage630PMSlot).toBeVisible();
  
    // set back to original (start 9:00 AM, end 5:00 PM) and save
    await availabilityPage.gotoAvailabilityPage();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await availabilityPage.bookingWindowInput.scrollIntoViewIfNeeded(); // scroll to btm for debug screenshots
    await availabilityPage.allStartTimeInput.fill('09:00');
    await availabilityPage.allEndTimeInput.fill('17:00');
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await availabilityPage.saveChangesBtn.scrollIntoViewIfNeeded();
    await availabilityPage.saveChangesBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await expect(availabilityPage.savedSuccessfullyText).toBeVisible();
  });
});
