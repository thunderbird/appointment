import { test, expect } from '@playwright/test';
import { AvailabilityPage } from '../../pages/availability-page';
import { BookingPage } from '../../pages/booking-page';
import { ensureWeAreSignedIn } from '../../utils/utils';

import {
  PLAYWRIGHT_TAG_E2E_DESKTOP_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,

  APPT_MY_SHARE_LINK,
  TIMEOUT_1_SECOND,
  TIMEOUT_3_SECONDS,
  TIMEOUT_10_SECONDS,
 } from '../../const/constants';

let availabilityPage: AvailabilityPage;
let bookApptPage: BookingPage;


test.describe('availability - booking page details on desktop browser', {
  tag: [PLAYWRIGHT_TAG_E2E_DESKTOP_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    await ensureWeAreSignedIn(page);
    // availability panel is displayed open as default
    bookApptPage = new BookingPage(page);
    availabilityPage = new AvailabilityPage(page);
    await availabilityPage.gotoAvailabilityPage();
  });

  test('able to change booking details on desktop browser', async ({ page }) => {
    await availabilityPage.bookingPageDetailsHdr.scrollIntoViewIfNeeded();
    await expect(availabilityPage.bookingPageDetailsHdr).toBeVisible();

    // page name and description fields enabled and editable
    await expect(availabilityPage.bookingPageNameInput).toBeEnabled();
    await expect(availabilityPage.bookingPageNameInput).toBeEditable();
    await expect(availabilityPage.bookingPageDescInput).toBeEnabled();
    await expect(availabilityPage.bookingPageDescInput).toBeEditable();

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

    // verify a 15 min slot now exists
    await bookApptPage.goForwardOneWeek();
    await expect.soft(bookApptPage.bookApptPage15MinSlot).toBeVisible();

    // change availability back
    await availabilityPage.gotoAvailabilityPage();
    await page.waitForTimeout(TIMEOUT_1_SECOND);

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

  test('verify booking page link on desktop browser', async ({ page }) => {
    await availabilityPage.bookingPageLinkHdr.scrollIntoViewIfNeeded();
    await expect(availabilityPage.bookingPageLinkHdr).toBeVisible();

    // click the refresh link button and then cancel out on the confirmation dialog, as we
    // don't want to actually change our share link as that would break the the E2E tests
    await availabilityPage.refreshLinkBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await expect(availabilityPage.refreshLinkConfirmTxt).toBeVisible();
    await availabilityPage.refreshLinkConfirmCancelBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);

    // verify booking page link displayed in 'share your link' is correct
    await availabilityPage.shareYourLinkInput.scrollIntoViewIfNeeded();
    expect(await availabilityPage.shareYourLinkInput.inputValue()).toBe(APPT_MY_SHARE_LINK);

    // ensure we can click the copy link button; we can't access the clipboard so can't verify
    await expect(availabilityPage.shareLinkCopyBtn).toBeEnabled();
    await availabilityPage.shareLinkCopyBtn.click();
  });
});
