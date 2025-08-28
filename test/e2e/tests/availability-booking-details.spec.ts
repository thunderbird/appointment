import { test, expect } from '@playwright/test';
import { AvailabilityPage } from '../pages/availability-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  TIMEOUT_1_SECOND,
 } from '../const/constants';

let availabilityPage: AvailabilityPage;

test.describe('availability - booking page details', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    // note: we are already signed into Appointment with our default settings (via our auth-setup)
    // availability panel is displayed open as default
    availabilityPage = new AvailabilityPage(page);
    await availabilityPage.gotoAvailabilityPage();
  });

  test('able to change booking page details', async ({ page }) => {
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
    await expect(availabilityPage.bookableToggle).toBeChecked();

    // now go to book appointment page (share link) and verify the changes took effect

    // todo: left off here
    // verify page name
    // verify page description
    // verify meeting duration (now have 15 minute time slots)

    // now go back to booking page settings and change back
    await availabilityPage.bookingPageNameInput.fill(origPageName);
    await availabilityPage.bookingPageDescInput.fill(origPageDesc);
    await availabilityPage.bookingPageMtgLinkInput.clear();
    await availabilityPage.bookingPageMtgDur30MinRadio.scrollIntoViewIfNeeded();
    await availabilityPage.bookingPageMtgDur30MinRadio.click();
    await availabilityPage.saveChangesBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
  });
});
