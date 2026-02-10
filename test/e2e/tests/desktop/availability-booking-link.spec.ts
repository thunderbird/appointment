import { test, expect } from '@playwright/test';
import { AvailabilityPage } from '../../pages/availability-page';
import { ensureWeAreSignedIn } from '../../utils/utils';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  APPT_MY_SHARE_LINK,
  TIMEOUT_1_SECOND,
 } from '../../const/constants';

let availabilityPage: AvailabilityPage;

test.describe('availability - booking page link on desktop browser', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    await ensureWeAreSignedIn(page);
    // availability panel is displayed open as default
    availabilityPage = new AvailabilityPage(page);
    await availabilityPage.gotoAvailabilityPage();
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
