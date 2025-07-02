import { test, expect } from '@playwright/test';
import { SettingsPage } from '../pages/settings-page';
import { DashboardPage } from '../pages/dashboard-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  APPT_LOGIN_EMAIL,
  APPT_DISPLAY_NAME,
  APPT_MY_SHARE_LINK,
 } from '../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('account settings - profile', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    // note: we are already signed into Appointment with our default settings (via our auth-setup)
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);

    // navigate to the account settings page
    await settingsPage.gotoAccountSettingsPage();
  });

  test('verify profile details', async ({ page }) => {
    // verify user name, preferred email, display name
    expect(await settingsPage.getAccountProfileUsername()).toBe(APPT_LOGIN_EMAIL);
    expect(await settingsPage.getAccountProfilePreferredEmail()).toBe(APPT_LOGIN_EMAIL);
    expect(await settingsPage.getAccountProfileDisplayName()).toBe(APPT_DISPLAY_NAME);

    // verify the displayed share link; there are two parts to the share link, a label that contains
    // the root URL (host and username), and an input field that contains an optional slug; note that
    // the label may not display the entire root URL as it is limited in size. Our test/e2e/.env
    // contains the full share link in APPT_MY_SHARE_LINK. Just verify that the first N chars of the
    // URL displayed in the share link label, and the optional input field value / slug are both
    // inside APPT_MY_SHARE_LINK.
    let shareLinkLabel = await settingsPage.profileMyLinkOptionalInput.innerText();
    expect(APPT_MY_SHARE_LINK).toContain(shareLinkLabel.substring(0, 10));
    let shareLinkOptionalSlug: string = await settingsPage.profileMyLinkOptionalInput.inputValue();
    if (shareLinkOptionalSlug.length) {
      expect(APPT_MY_SHARE_LINK).toContain(shareLinkOptionalSlug);
    }
  });

  test('able to change display name', async ({ page }) => {
    // change the account settings user display name and save; we use expect.soft here because if the expect
    // fails we still want the test to continue so that the test will change the setting back to original
    // value (expect.soft will still mark the test case failed if the expect fails, but won't stop the test)
    const newDisplayName: string = 'Display name modified by E2E!'
    await settingsPage.setAccountProfileDisplayName(newDisplayName);
    expect.soft(await settingsPage.getAccountProfileDisplayName()).toBe(newDisplayName);

    // now change the display name setting back to what it was before, and save
    await settingsPage.gotoAccountSettingsPage();
    await settingsPage.setAccountProfileDisplayName(APPT_DISPLAY_NAME);
    expect(await settingsPage.getAccountProfileDisplayName()).toBe(APPT_DISPLAY_NAME);
  });

  test('refresh link button', async ({ page }) => {
    // verify that clicking the refresh link button results in a refresh link confirm dialog
    // won't actually refresh the link as that would break the other E2E tests
    await expect(settingsPage.refreshLinkBtn).toBeEnabled();
    await settingsPage.refreshLinkBtn.click();
    await settingsPage.confirmRefreshCancelBtn.click();
  });
});
