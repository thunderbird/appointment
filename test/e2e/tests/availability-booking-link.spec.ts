import { test, expect } from '@playwright/test';
import { AvailabilityPage } from '../pages/availability-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  APPT_MY_SHARE_LINK,
  TIMEOUT_1_SECOND,
 } from '../const/constants';

let availabilityPage: AvailabilityPage;

test.describe('availability - booking page link', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    // note: we are already signed into Appointment with our default settings (via our auth-setup)
    // availability panel is displayed open as default
    availabilityPage = new AvailabilityPage(page);
    await availabilityPage.gotoAvailabilityPage();
  });

  test('verify booking page link', async ({ page }) => {
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

    // click the button to copy the booking page link and verify copied link is correct
    // note: we can't access clipboard in firefox b/c of security so instead we will:
    //  - get the contents of the 'share your link' input field (correct link)
    //  - click the copy link button
    //  - clear the 'share your link' input field so it is empty
    //  - focus on the empty 'share your link' input field
    //  - do a keyboard paste into the field
    //  - retrieve the new contents of the 'share your link' input after the paste into that field
    //  - verify the input field now has the correct link url
    const correctBookingUrl = await availabilityPage.shareYourLinkInput.inputValue();
    await availabilityPage.shareLinkCopyBtn.click();
    await availabilityPage.shareYourLinkInput.clear();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await availabilityPage.shareYourLinkInput.focus();
    await page.keyboard.press('ControlOrMeta+V');
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    const afterPasteBookingUrl = await availabilityPage.shareYourLinkInput.inputValue();
    expect(afterPasteBookingUrl).toEqual(correctBookingUrl);
  });
});
