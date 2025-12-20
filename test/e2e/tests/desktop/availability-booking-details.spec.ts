import { test, expect } from '@playwright/test';
import { AvailabilityPage } from '../../pages/availability-page';
import { BookingPage } from '../../pages/booking-page';
import { ensureWeAreSignedIn } from '../../utils/utils';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  APPT_TIMEZONE_SETTING_PRIMARY,
  APPT_MY_SHARE_LINK,
  TIMEOUT_1_SECOND,
  TIMEOUT_3_SECONDS,
  TIMEOUT_10_SECONDS,
 } from '../../const/constants';

let availabilityPage: AvailabilityPage;
let bookApptPage: BookingPage;
let origPageName: string;
let origPageDesc: string;


test.describe('availability - booking page details on desktop browser', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    await ensureWeAreSignedIn(page);
    // availability panel is displayed open as default
    bookApptPage = new BookingPage(page);
    availabilityPage = new AvailabilityPage(page);
    await availabilityPage.gotoAvailabilityPage();
  });

  // the share link (request a booking page) will display in the local browser context timezone but the main
  // appointment account settings could be a different timezone; set the browser context to always be in
  // the primary timezone
  test.use({
    timezoneId: APPT_TIMEZONE_SETTING_PRIMARY,
  });

  test('able to change booking details on desktop browser', async ({ page }) => {
    await availabilityPage.bookingPageDetailsHdr.scrollIntoViewIfNeeded();
    await expect(availabilityPage.bookingPageDetailsHdr).toBeVisible();

    // change page name (use current date/time value so can verify was changed by this test)
    origPageName = await availabilityPage.bookingPageNameInput.inputValue();
    const newPageName = `Page name modified by E2E test at ${new Date().toDateString()}`;
    await availabilityPage.bookingPageNameInput.fill(newPageName);

    // add a page description (again use current date/time in there too so can verify was changed by this test)
    origPageDesc = await availabilityPage.bookingPageDescInput.inputValue();
    const newPageDesc = `Page description modified by E2E test at ${new Date().toDateString}`;
    await availabilityPage.bookingPageDescInput.fill(newPageDesc);

    // able to type in a virtual meeting link
    await availabilityPage.bookingPageMtgLinkInput.scrollIntoViewIfNeeded();
    await availabilityPage.bookingPageMtgLinkInput.fill(`fake.meeting.link?id=${Date.now()}`);

    // change the meeting duration to 15 min
    await availabilityPage.bookingPageMtgDur15MinBtn.scrollIntoViewIfNeeded();
    await availabilityPage.bookingPageMtgDur15MinBtn.click();

    // save the changes
    await availabilityPage.saveChangesBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);

    // now go to book appointment page (share link) and verify the changes took effect
    await page.goto(APPT_MY_SHARE_LINK);
    await page.waitForTimeout(TIMEOUT_3_SECONDS);

    // page name and description
    expect.soft(await bookApptPage.titleText.innerText()).toEqual(newPageName);
    const pageDescLocator = page.getByText(newPageDesc, { exact: true });
    await expect.soft(pageDescLocator).toBeVisible();

    // verify a 15 min slot now exists
    await bookApptPage.goForwardOneWeek();
    await expect.soft(bookApptPage.bookApptPage15MinSlot).toBeVisible();

    // change availability back
    await availabilityPage.gotoAvailabilityPage();
    await page.waitForTimeout(TIMEOUT_1_SECOND);

    await availabilityPage.bookingPageNameInput.fill(origPageName);
    await availabilityPage.bookingPageDescInput.fill(origPageDesc);
    await availabilityPage.bookingPageMtgLinkInput.clear();
    await availabilityPage.bookingPageMtgDur30MinBtn.scrollIntoViewIfNeeded();
    await availabilityPage.bookingPageMtgDur30MinBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);

    const saveBtnVisible = await availabilityPage.saveChangesBtn.isVisible({ timeout: TIMEOUT_10_SECONDS });

    if (saveBtnVisible) {
      await availabilityPage.saveChangesBtn.click();
      await page.waitForTimeout(TIMEOUT_1_SECOND);
    }
  });
});
