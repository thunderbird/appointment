import { test, expect } from '@playwright/test';
import { SettingsPage } from '../../pages/settings-page';
import { DashboardPage } from '../../pages/dashboard-page';
import { ensureWeAreSignedIn } from '../../utils/utils';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  TIMEOUT_1_SECOND,
  TIMEOUT_30_SECONDS,
 } from '../../const/constants';

let settingsPage: SettingsPage;
let dashboardPage: DashboardPage;

test.describe('connected applications settings on desktop browser', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    await ensureWeAreSignedIn(page);
    settingsPage = new SettingsPage(page);
    dashboardPage = new DashboardPage(page);
    // navigate to the settings page, connected apps section
    await settingsPage.gotoConnectedAppSettings();
  });

  test('verify connected applications settings on desktop browser', async ({ page }) => {
    // verify section header
    await expect(settingsPage.connectedAppsHdr).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await settingsPage.connectedAppsHdr.scrollIntoViewIfNeeded();

    // one of the calendars is marked with the default badge; if there is more than one badge found this will fail
    await expect(settingsPage.defaultCalendarBadge).toBeVisible();
    await settingsPage.defaultCalendarBadge.scrollIntoViewIfNeeded();

    // verify that clicking the 'add caldav' button brings up the caldav connection dialog; just close it
    await settingsPage.addCaldavBtn.waitFor({ state: 'visible', timeout: TIMEOUT_30_SECONDS });
    await settingsPage.addCaldavBtn.scrollIntoViewIfNeeded();
    await settingsPage.addCaldavBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    await expect(settingsPage.addCaldavUsernameInput).toBeVisible();
    await expect(settingsPage.addCaldavLocationInput).toBeVisible();
    await expect(settingsPage.addCaldavPasswordInput).toBeVisible();
    await settingsPage.addCaldavCloseModalBtn.click();
    await page.waitForTimeout(TIMEOUT_1_SECOND);

    // verify clicking the 'add google calendar' button brings up the google sign-in url
    await settingsPage.addGoogleBtn.waitFor({ state: 'visible', timeout: TIMEOUT_30_SECONDS });
    await settingsPage.addGoogleBtn.click();
    await expect(settingsPage.googleSignInHdr).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await settingsPage.gotoConnectedAppSettings();
  });

  test('verify calendar dropdown only shows for calendars with different external connection than default', async ({ page }) => {
    // verify section header and default badge
    await expect(settingsPage.connectedAppsHdr).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await expect(settingsPage.defaultCalendarBadge).toBeVisible();
    await settingsPage.defaultCalendarBadge.scrollIntoViewIfNeeded();

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
      await settingsPage.calendarDropdownTriggers.first().scrollIntoViewIfNeeded();
      await settingsPage.calendarDropdownTriggers.first().click();
      await page.waitForTimeout(TIMEOUT_1_SECOND);

      // Verify dropdown menu options are visible for non-default-connection calendars
      await expect(settingsPage.calendarDropdownSetAsDefault).toBeVisible();
      await expect(settingsPage.calendarDropdownDisconnect).toBeVisible();

      // Close the dropdown by pressing Escape
      await page.keyboard.press('Escape');
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
    await targetCheckbox.scrollIntoViewIfNeeded();
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
});
