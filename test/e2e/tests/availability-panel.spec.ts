import { test, expect } from '@playwright/test';
import { DashboardPage } from '../pages/dashboard-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  APPT_DISPLAY_NAME,
  TIMEOUT_60_SECONDS,
 } from '../const/constants';
import exp from 'constants';

let dashboardPage: DashboardPage;

test.describe('availability panel', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    // note: we are already signed into Appointment with our default settings (via our auth-setup)
    dashboardPage = new DashboardPage(page);

    // availability panel is displayed open as default on the dashboard
    await dashboardPage.gotoToDashboardMonthView();
  });

  test('default availability settings are displayed', async ({ page }) => {
    // just verify that the default availability options are available/displayed
    // timzone display is covered in other tests so not checked here
    expect(await dashboardPage.getAvailabilityPanelHeader()).toContain(APPT_DISPLAY_NAME);
    await expect(dashboardPage.setAvailabilityText).toBeVisible();
    await expect(dashboardPage.customizePerDayCheckBox).toBeVisible();
    await expect(dashboardPage.customizePerDayCheckBox).toBeEnabled();

    // if customize per day checkbox is NOT turned on then we will see overall start and end time inputs
    const customize_day = await dashboardPage.customizePerDayCheckBox.isChecked();
    if (!customize_day) {
      await expect(dashboardPage.allStartTimeInput).toBeVisible();
      await expect(dashboardPage.allStartTimeInput).toBeEnabled();
      await expect(dashboardPage.allEndTimeInput).toBeVisible();
      await expect(dashboardPage.allEndTimeInput).toBeEnabled();
    }

    await dashboardPage.editLinkBtn.scrollIntoViewIfNeeded();
    await expect(dashboardPage.editLinkBtn).toBeVisible();
    await expect(dashboardPage.editLinkBtn).toBeEnabled();
  });

  test('customize-per-day checkbox reveals daily time slots', async ({ page }) => {
    // get current status of customize per day check box (so this test will run regardless of state)
    await expect(dashboardPage.customizePerDayCheckBox).toBeVisible({ timeout: TIMEOUT_60_SECONDS });
    await expect(dashboardPage.customizePerDayCheckBox).toBeEnabled({ timeout: TIMEOUT_60_SECONDS });

    const customize_per_day = await dashboardPage.customizePerDayCheckBox.isChecked();

    if (!customize_per_day) {
      // is off, turn it on, verify daily time slot options appear
      await dashboardPage.turnOnCustomizePerDayAndVerify();
      await dashboardPage.turnOffCustomizePerDayAndVerify();
    } else {
      // is on already, turn it off, verify daily time slot options aren't visible
      await dashboardPage.turnOffCustomizePerDayAndVerify();
      await dashboardPage.turnOnCustomizePerDayAndVerify();
    }
  });
});
