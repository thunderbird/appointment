import { test, expect } from '@playwright/test';
import { SettingsPage } from '../../pages/settings-page';
import { DashboardPage } from '../../pages/dashboard-page';
import { mobileSignInAndSetup } from '../../utils/utils';

import {
  PLAYWRIGHT_TAG_E2E_SUITE_MOBILE,
  PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY,
  TIMEOUT_1_SECOND,
  TIMEOUT_3_SECONDS,
  TIMEOUT_30_SECONDS,
 } from '../../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('settings - connected applications on mobile browser', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE_MOBILE, PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }, testInfo) => {
    settingsPage = new SettingsPage(page, testInfo.project.name); // i.e. 'ios-safari'
    dashboardPage = new DashboardPage(page);

    // mobile browsers don't support saving auth storage state so must sign in before each test
    // send in the playright test project name i.e. safari-ios because some mobile platforms differ
    await mobileSignInAndSetup(page, testInfo.project.name);

    // navigate to the settings page, connected apps section
    await settingsPage.gotoConnectedAppSettings();
    await page.waitForTimeout(TIMEOUT_3_SECONDS);
  });

  test.afterEach(async ({ page }) => {
    // close the browser page when we're done so it doesn't stay as a tab on mobile browser
    await page.close();
  });

  test('verify connected applications settings on mobile browser', async ({ page }) => {
    // verify section header
    await expect(settingsPage.connectedAppsHdr).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await settingsPage.scrollIntoView(settingsPage.connectedAppsHdr);

    // one of the calendars is marked with the default badge; if there is more than one badge found this will fail
    await expect(settingsPage.defaultCalendarBadge).toBeVisible();
    await settingsPage.scrollIntoView(settingsPage.defaultCalendarBadge);

    // verify that clicking the 'add caldav' button brings up the caldav connection dialog; just close it
    await settingsPage.scrollIntoView(settingsPage.addCaldavBtn);
    await settingsPage.addCaldavBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await expect(settingsPage.addCaldavUsernameInput).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await settingsPage.scrollIntoView(settingsPage.addCaldavUsernameInput);
    await expect(settingsPage.addCaldavLocationInput).toBeVisible();
    await expect(settingsPage.addCaldavPasswordInput).toBeVisible();

    // on android mobile browser there is no close button for the add caldav dialog (issue 1250)
    // so to continue this test go back to the settings URL / refresh the page to close the add caldav dialog
    await settingsPage.gotoConnectedAppSettings();
    await page.waitForTimeout(TIMEOUT_3_SECONDS);

    // verify clicking the 'add google calendar' button brings up the google sign-in url
    await settingsPage.addGoogleBtn.click();
    await expect(settingsPage.googleSignInHdr).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
  });

  test('verify calendar dropdown only shows for calendars with different external connection than default', async ({ page }) => {
    // verify section header and default badge
    await expect(settingsPage.connectedAppsHdr).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await expect(settingsPage.defaultCalendarBadge).toBeVisible();
    await settingsPage.scrollIntoView(settingsPage.defaultCalendarBadge);

    // Get all calendar checkboxes to count total calendars
    const calendarCheckboxes = page.locator('.calendars-container input[type="checkbox"]');
    const totalCalendars = await calendarCheckboxes.count();

    // Get all dropdown triggers (only visible for calendars with different ExternalConnection than default)
    const dropdownCount = await settingsPage.calendarDropdownTriggers.count();

    // There should be fewer dropdowns than total calendars since calendars sharing
    // the same ExternalConnection as the default calendar won't have dropdowns
    expect(dropdownCount).toBeLessThan(totalCalendars);

    // If there are any dropdown triggers visible, verify the dropdown menu works
    if (dropdownCount > 0) {
      await settingsPage.scrollIntoView(settingsPage.calendarDropdownTriggers.first());
      await settingsPage.calendarDropdownTriggers.first().click();
      await page.waitForTimeout(TIMEOUT_1_SECOND);

      // Verify dropdown menu options are visible for non-default-connection calendars
      await expect(settingsPage.calendarDropdownSetAsDefault).toBeVisible();
      await expect(settingsPage.calendarDropdownDisconnect).toBeVisible();

      // Close the dropdown by tapping elsewhere
      await settingsPage.connectedAppsHdr.click();
      await page.waitForTimeout(TIMEOUT_1_SECOND);
    }
  });

  test('verify calendar checkbox change shows notice bar and revert restores previous state', async ({ page }) => {
    // verify section header
    await expect(settingsPage.connectedAppsHdr).toBeVisible({ timeout: TIMEOUT_30_SECONDS });

    // Find the first non-disabled calendar checkbox (not the default calendar)
    const nonDisabledCheckboxes = settingsPage.calendarCheckboxes.filter({ has: page.locator(':not([disabled])') });
    const checkboxCount = await nonDisabledCheckboxes.count();

    // Skip test if there are no non-disabled checkboxes
    if (checkboxCount === 0) {
      test.skip();
      return;
    }

    // Get the first non-disabled checkbox and record its initial state
    const targetCheckbox = nonDisabledCheckboxes.first();
    await settingsPage.scrollIntoView(targetCheckbox);
    const initialCheckedState = await targetCheckbox.isChecked();

    // Verify notice bar is NOT visible before making changes
    await expect(settingsPage.unsavedChangesNotice).not.toBeVisible();

    // Click the checkbox to toggle its state
    await targetCheckbox.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);

    // Verify the checkbox state has changed
    const newCheckedState = await targetCheckbox.isChecked();
    expect(newCheckedState).toBe(!initialCheckedState);

    // Verify the notice bar appears with "You have unsaved changes"
    await expect(settingsPage.unsavedChangesNotice).toBeVisible({ timeout: TIMEOUT_30_SECONDS });

    // Verify the "Revert changes" button is visible
    await expect(settingsPage.revertBtn).toBeVisible();

    // Click the "Revert changes" button
    await settingsPage.revertBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);

    // Verify the checkbox is restored to its original state
    const restoredCheckedState = await targetCheckbox.isChecked();
    expect(restoredCheckedState).toBe(initialCheckedState);

    // Verify the notice bar disappears after reverting
    await expect(settingsPage.unsavedChangesNotice).not.toBeVisible();
  });

  test.afterAll(async ({ browser }, testInfo) => {
    // close the browser when we're done (good practice for BrowserStack); only do this for BrowserStack,
    // because if we do this when running on a local playwright mobile viewport the tests will fail
    if (!testInfo.project.name.includes('View')) {
      await browser.close();
    }
  });
});
