import { test, expect, mergeExpects } from '@playwright/test';
import { AvailabilityPage } from '../pages/availability-page';
import { BookingPage } from '../pages/booking-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  APPT_MY_SHARE_LINK,
  TIMEOUT_1_SECOND,
  TIMEOUT_3_SECONDS,
 } from '../const/constants';

let availabilityPage: AvailabilityPage;
let bookApptPage: BookingPage;

test.describe('availability - booking page details', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    // note: we are already signed into Appointment with our default settings (via our auth-setup)
    // availability panel is displayed open as default
    bookApptPage = new BookingPage(page);
    availabilityPage = new AvailabilityPage(page);
    await availabilityPage.gotoAvailabilityPage();
  });

  test('able to change booking details', async ({ page }) => {
    await availabilityPage.bookingPageDetailsHdr.scrollIntoViewIfNeeded();
    await expect(availabilityPage.bookingPageDetailsHdr).toBeVisible();

    // change page name (use current date/time value so can verify was changed by this test)
    const origPageName = await availabilityPage.bookingPageNameInput.inputValue();
    const newPageName = `Page name modified by E2E test at ${Date.now()}`;
    await availabilityPage.bookingPageNameInput.fill(newPageName);

    // add a page description (again use current date/time in there too so can verify was changed by this test)
    const origPageDesc = await availabilityPage.bookingPageDescInput.inputValue();
    const newPageDesc = `Page description modified by E2E test at ${Date.now()}`;
    await availabilityPage.bookingPageDescInput.fill(newPageDesc);

    // able to type in a virtual meeting link
    await availabilityPage.bookingPageMtgLinkInput.scrollIntoViewIfNeeded();
    await availabilityPage.bookingPageMtgLinkInput.fill(`fake.meeting.link?id=${Date.now()}`);

    // change the meeting duration to 15 min
    await availabilityPage.bookingPageMtgDur15MinRadio.scrollIntoViewIfNeeded();
    await availabilityPage.bookingPageMtgDur15MinRadio.click();

    // save the changes
    await availabilityPage.saveChangesBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);

    // now go to book appointment page (share link) and verify the changes took effect
    // we use expect.soft here so that we ensure even on a failure the test will continue
    // so that the booking page details will be set back to what they were before
    await page.goto(APPT_MY_SHARE_LINK);
    await page.waitForTimeout(TIMEOUT_3_SECONDS);

    // page name and description
    expect.soft(await bookApptPage.titleText.innerText()).toEqual(newPageName);
    const pageDescLocator = page.getByText(newPageDesc, { exact: true });
    await expect.soft(pageDescLocator).toBeVisible();

    // verify a 15 min slot now exists
    await expect(bookApptPage.bookApptPage15MinSlot).toBeVisible();

    // now go back to booking page settings and change back
    await availabilityPage.gotoAvailabilityPage();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await availabilityPage.bookingPageNameInput.fill(origPageName);
    await availabilityPage.bookingPageDescInput.fill(origPageDesc);
    await availabilityPage.bookingPageMtgLinkInput.clear();
    await availabilityPage.bookingPageMtgDur30MinRadio.scrollIntoViewIfNeeded();
    await availabilityPage.bookingPageMtgDur30MinRadio.click();
    await availabilityPage.saveChangesBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
  });
});
