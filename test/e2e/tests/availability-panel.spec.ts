import { test, expect } from '@playwright/test';
import { AvailabilityPage } from '../pages/availability-page';

import {
  PLAYWRIGHT_TAG_E2E_SUITE,
  PLAYWRIGHT_TAG_PROD_NIGHTLY,
  APPT_DISPLAY_NAME,
  TIMEOUT_60_SECONDS,
 } from '../const/constants';

let availabilityPage: AvailabilityPage;

test.describe('availability panel', {
  tag: [PLAYWRIGHT_TAG_E2E_SUITE, PLAYWRIGHT_TAG_PROD_NIGHTLY],
}, () => {
  test.beforeEach(async ({ page }) => {
    // note: we are already signed into Appointment with our default settings (via our auth-setup)
    // availability panel is displayed open as default
    availabilityPage = new AvailabilityPage(page);
    await availabilityPage.gotoAvailabilityPage();
  });

  test('default availability settings are displayed', async () => {
    // just verify that the default availability options are available/displayed
    // timzone display is covered in other tests so not checked here
    expect(await availabilityPage.getAvailabilityPanelHeader()).toContain(APPT_DISPLAY_NAME);
    await expect(availabilityPage.setAvailabilityText).toBeVisible();
    await expect(availabilityPage.customizePerDayCheckBox).toBeVisible();
    await expect(availabilityPage.customizePerDayCheckBox).toBeEnabled();

    // if customize per day checkbox is NOT turned on then we will see overall start and end time inputs
    const customize_day = await availabilityPage.customizePerDayCheckBox.isChecked();
    if (!customize_day) {
      await expect(availabilityPage.allStartTimeInput).toBeVisible();
      await expect(availabilityPage.allStartTimeInput).toBeEnabled();
      await expect(availabilityPage.allEndTimeInput).toBeVisible();
      await expect(availabilityPage.allEndTimeInput).toBeEnabled();
    }

    await availabilityPage.editLinkBtn.scrollIntoViewIfNeeded();
    await expect(availabilityPage.editLinkBtn).toBeVisible();
    await expect(availabilityPage.editLinkBtn).toBeEnabled();
  });

  test('customize-per-day checkbox reveals daily time slots', async () => {
    // get current status of customize per day check box (so this test will run regardless of state)
    await expect(availabilityPage.customizePerDayCheckBox).toBeVisible({ timeout: TIMEOUT_60_SECONDS });
    await expect(availabilityPage.customizePerDayCheckBox).toBeEnabled({ timeout: TIMEOUT_60_SECONDS });

    const customize_per_day = await availabilityPage.customizePerDayCheckBox.isChecked();

    if (!customize_per_day) {
      // is off, turn it on, verify daily time slot options appear
      await availabilityPage.turnOnCustomizePerDayAndVerify();
      await availabilityPage.turnOffCustomizePerDayAndVerify();
    } else {
      // is on already, turn it off, verify daily time slot options aren't visible
      await availabilityPage.turnOffCustomizePerDayAndVerify();
      await availabilityPage.turnOnCustomizePerDayAndVerify();
    }
  });
});
