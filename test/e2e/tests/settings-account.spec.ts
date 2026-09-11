import { test, expect } from '@playwright/test';
import { AvailabilityPage } from '../pages/availability-page';
import { SettingsPage } from '../pages/settings-page';
import { ensureWeAreSignedIn, getTestPlatform, mobileSignInAndSetup } from '../utils/utils';

import {
  APPT_MY_SHARE_LINK,
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_E2E_SUITE_MOBILE,
  PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  TIMEOUT_1_SECOND,
  TIMEOUT_3_SECONDS,
  TIMEOUT_30_SECONDS,
} from '../const/constants';

let settingsPage: SettingsPage;
let availabilityPage: AvailabilityPage;

test.describe('account settings', {
  // Preserve the union of the former desktop and mobile suite tags so this
  // common source continues to run in all four existing workflows.
  tag: [
    PLAYWRIGHT_TAG_E2E_SUITE,
    PLAYWRIGHT_TAG_PROD_NIGHTLY,
    PLAYWRIGHT_TAG_E2E_SUITE_MOBILE,
    PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY,
  ],
}, () => {
  test.beforeEach(async ({ page }, testInfo) => {
    const projectName = testInfo.project.name;
    const testPlatform = getTestPlatform(projectName);

    // Passing the project name lets SettingsPage avoid scrolling operations
    // that BrowserStack's Playwright implementation does not support on iOS.
    settingsPage = new SettingsPage(page, projectName);
    availabilityPage = new AvailabilityPage(page);

    if (testPlatform === 'desktop') {
      // Desktop projects load the storage state created by
      // auth.desktop.setup.ts. Revalidate that session before every test in
      // case a long suite run allowed it to expire.
      await ensureWeAreSignedIn(page);
    } else {
      // BrowserStack mobile projects cannot load the saved desktop storage
      // state. They must sign in and restore the expected default settings for
      // every test, with the project name preserving Android/iOS workarounds.
      await mobileSignInAndSetup(page, projectName);
    }

    await settingsPage.gotoAccountSettings();

    if (testPlatform !== 'desktop') {
      // Real mobile devices need extra time for the account-settings controls
      // to settle after navigation. Preserve the wait from the mobile spec.
      await page.waitForTimeout(TIMEOUT_3_SECONDS);
    }
  });

  test.afterEach(async ({ page }, testInfo) => {
    // Close pages created for mobile tests so they do not remain open as tabs
    // on BrowserStack devices. Desktop fixtures manage their own page lifetime.
    if (getTestPlatform(testInfo.project.name) !== 'desktop') {
      await page.close();
    }
  });

  test('verify account settings', async ({ page }, testInfo) => {
    const testPlatform = getTestPlatform(testInfo.project.name);

    await expect(settingsPage.accountSettingsHeader).toBeVisible();

    // BrowserStack iOS supports the locator query `isEnabled`, but not every
    // Playwright enabled-state matcher. Use the query consistently here so the
    // same assertion works on all platforms.
    await expect(settingsPage.displayNameInput).toBeVisible();
    expect(await settingsPage.displayNameInput.isEnabled()).toBeTruthy();

    await settingsPage.scrollIntoView(settingsPage.bookingPageURLInput);
    expect(await settingsPage.bookingPageURLInput.inputValue()).toBe(APPT_MY_SHARE_LINK);

    // Firefox does not permit clipboard inspection in this suite, so verify
    // only that Copy can be invoked. BrowserStack iOS does not support the
    // enabled assertion used here; retain the click but skip that assertion.
    await settingsPage.scrollIntoView(settingsPage.copyLinkBtn);
    if (testPlatform !== 'ios') {
      expect(await settingsPage.copyLinkBtn.isEnabled()).toBeTruthy();
    }
    await settingsPage.copyLinkBtn.click();

    // Do not download account data because it may leave sensitive artifacts
    // on the test runner. Mobile historically verifies visibility only, while
    // desktop also verifies that the control is enabled.
    await settingsPage.scrollIntoView(settingsPage.downloadDataBtn);
    await expect(settingsPage.downloadDataBtn).toBeVisible();
    if (testPlatform === 'desktop') {
      await expect(settingsPage.downloadDataBtn).toBeEnabled();
    }

    // Exercise the destructive action only far enough to verify its safety
    // confirmation, then cancel without deleting any Appointment data.
    await settingsPage.scrollIntoView(settingsPage.deleteDataBtn);
    await settingsPage.deleteDataBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await settingsPage.scrollIntoView(settingsPage.deleteDataConfirmCancelBtn);
    await settingsPage.deleteDataConfirmCancelBtn.click({ timeout: TIMEOUT_30_SECONDS });
    await page.waitForTimeout(TIMEOUT_1_SECOND);

    // Desktop retains its explicit URL assertion. Mobile relies on the page
    // content because navigation behavior differs on the BrowserStack devices.
    await settingsPage.scrollIntoView(settingsPage.manageBookingLink);
    await settingsPage.manageBookingLink.click();
    if (testPlatform === 'desktop') {
      await page.waitForURL('**/availability');
    }
    await expect(availabilityPage.setAvailabilityText).toBeVisible();
  });

  test.afterAll(async ({ browser }, testInfo) => {
    const projectName = testInfo.project.name;
    const testPlatform = getTestPlatform(projectName);
    const isLocalMobileView = projectName.toLowerCase().includes('view');

    // Explicitly close BrowserStack real-device sessions when this spec is
    // complete. Closing the browser breaks subsequent tests when using the
    // local Playwright mobile viewport, so leave `*-View` projects open.
    if (testPlatform !== 'desktop' && !isLocalMobileView) {
      await browser.close();
    }
  });
});
