import { test, expect, type Page } from '@playwright/test';
import { SettingsPage } from '../pages/settings-page';
import { ensureWeAreSignedIn, getTestPlatform, mobileSignInAndSetup } from '../utils/utils';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_E2E_SUITE_MOBILE,
  PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  TIMEOUT_1_SECOND,
  TIMEOUT_3_SECONDS,
  TIMEOUT_30_SECONDS,
} from '../const/constants';

let settingsPage: SettingsPage;

/**
 * Authenticate for the current platform and open Connected Applications.
 * Keeping setup in a helper lets the desktop-only dropdown test skip mobile
 * from its test body before any sign-in or navigation work is performed.
 */
const setupConnectedApps = async (page: Page, projectName: string) => {
  const testPlatform = getTestPlatform(projectName);

  // Pass the exact project name to SettingsPage so its scroll helper can avoid
  // unsupported scrollIntoViewIfNeeded calls on BrowserStack iOS.
  settingsPage = new SettingsPage(page, projectName);

  if (testPlatform === 'desktop') {
    // Desktop projects reuse the auth state prepared by auth.desktop.setup.ts
    // and revalidate it in case a long suite allowed the session to expire.
    await ensureWeAreSignedIn(page);
  } else {
    // Real mobile projects cannot load desktop storage state, so authenticate
    // and restore the suite's expected default settings before every test.
    await mobileSignInAndSetup(page, projectName);
  }

  await settingsPage.gotoConnectedAppSettings();

  if (testPlatform !== 'desktop') {
    // Preserve the additional settling time used by real mobile devices after
    // navigating to the Connected Applications section.
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
  }
};

test.describe('connected applications settings', {
  // Preserve the union of the former desktop and mobile tags so the common
  // source continues to run in regular and nightly suites on both platforms.
  tag: [
    PLAYWRIGHT_TAG_E2E_SUITE,
    PLAYWRIGHT_TAG_PROD_NIGHTLY,
    PLAYWRIGHT_TAG_E2E_SUITE_MOBILE,
    PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY,
  ],
}, () => {
  test.afterEach(async ({ page }, testInfo) => {
    // Close mobile pages so they do not remain open as tabs on BrowserStack.
    // Desktop fixtures manage their own page lifetime.
    if (getTestPlatform(testInfo.project.name) !== 'desktop') {
      await page.close();
    }
  });

  test('verify connected applications settings', async ({ page }, testInfo) => {
    const projectName = testInfo.project.name;
    const testPlatform = getTestPlatform(projectName);
    await setupConnectedApps(page, projectName);

    await expect(settingsPage.connectedAppsHdr).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await settingsPage.scrollIntoView(settingsPage.connectedAppsHdr);

    // Exactly one connected calendar should be identified as the default. The
    // Playwright assertion fails if this locator resolves to multiple badges.
    await expect(settingsPage.defaultCalendarBadge).toBeVisible();
    await settingsPage.scrollIntoView(settingsPage.defaultCalendarBadge);

    // Open the CalDAV dialog and verify its required connection fields without
    // submitting credentials or creating another external connection.
    await settingsPage.addCaldavBtn.waitFor({ state: 'visible', timeout: TIMEOUT_30_SECONDS });
    await settingsPage.scrollIntoView(settingsPage.addCaldavBtn);
    await settingsPage.addCaldavBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await expect(settingsPage.addCaldavUsernameInput).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await settingsPage.scrollIntoView(settingsPage.addCaldavUsernameInput);
    await expect(settingsPage.addCaldavLocationInput).toBeVisible();
    await expect(settingsPage.addCaldavPasswordInput).toBeVisible();

    if (testPlatform === 'desktop') {
      // Desktop exposes a working close control for the CalDAV modal.
      await settingsPage.addCaldavCloseModalBtn.click();
      await page.waitForTimeout(TIMEOUT_1_SECOND);
    } else {
      // Android does not expose the CalDAV close button (issue 1250). Reloading
      // the Connected Applications route closes the modal reliably on both
      // mobile platforms and keeps their shared flow consistent.
      await settingsPage.gotoConnectedAppSettings();
      await page.waitForTimeout(TIMEOUT_3_SECONDS);
    }

    // The test verifies only that Google authentication opens; it does not
    // provide Google credentials or create another calendar connection.
    await settingsPage.addGoogleBtn.waitFor({ state: 'visible', timeout: TIMEOUT_30_SECONDS });
    await settingsPage.addGoogleBtn.click();
    await expect(settingsPage.googleSignInHdr).toBeVisible({ timeout: TIMEOUT_30_SECONDS });

    if (testPlatform === 'desktop') {
      // Return desktop to Appointment after the external sign-in assertion.
      // Mobile closes its page in afterEach, so no return navigation is needed.
      await settingsPage.gotoConnectedAppSettings();
    }
  });

  test.describe('calendar connection dropdown', () => {
    // Locator collection operations used below are not supported by the
    // BrowserStack iOS Playwright implementation. Keep this existing coverage
    // desktop-only. The body-level skip has access to testInfo and runs before
    // the explicit setup helper, so mobile does no authentication work here.

    test('only shows for calendars with a different external connection than the default', async ({ page }, testInfo) => {
      test.skip(
        getTestPlatform(testInfo.project.name) !== 'desktop',
        'Calendar collection assertions are supported only on desktop browsers',
      );
      await setupConnectedApps(page, testInfo.project.name);

      await expect(settingsPage.connectedAppsHdr).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
      await expect(settingsPage.defaultCalendarBadge).toBeVisible();
      await settingsPage.scrollIntoView(settingsPage.defaultCalendarBadge);

      // A calendar sharing the default calendar's ExternalConnection must not
      // expose a connection-level dropdown. Therefore dropdowns must be fewer
      // than the total number of connected calendars.
      const totalCalendars = await settingsPage.calendarCheckboxes.count();
      const dropdownCount = await settingsPage.calendarDropdownTriggers.count();
      expect(dropdownCount).toBeLessThan(totalCalendars);

      if (dropdownCount > 0) {
        await settingsPage.scrollIntoView(settingsPage.calendarDropdownTriggers.first());
        await settingsPage.calendarDropdownTriggers.first().click();
        await page.waitForTimeout(TIMEOUT_1_SECOND);
        await expect(settingsPage.calendarDropdownSetAsDefault).toBeVisible();

        // Close the menu without changing the default calendar.
        await page.keyboard.press('Escape');
        await page.waitForTimeout(TIMEOUT_1_SECOND);
      }
    });
  });

  test.afterAll(async ({ browser }, testInfo) => {
    const projectName = testInfo.project.name;
    const testPlatform = getTestPlatform(projectName);
    const isLocalMobileView = projectName.toLowerCase().includes('view');

    // Close BrowserStack real-device sessions after this spec. Closing the
    // browser for the local `*-View` project breaks later emulated-mobile tests.
    if (testPlatform !== 'desktop' && !isLocalMobileView) {
      await browser.close();
    }
  });
});
