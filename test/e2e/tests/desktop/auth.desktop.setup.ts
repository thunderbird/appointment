import { test as setup, expect } from '@playwright/test';
import { AvailabilityPage } from '../../pages/availability-page';
import path from 'path';

import { navigateToAppointmentAndSignIn, setDefaultUserSettingsLocalStore } from '../../utils/utils';

import {
    APPT_DASHBOARD_HOME_PAGE,
    APPT_SETTINGS_PAGE,
    APPT_DISPLAY_NAME,
    TIMEOUT_1_SECOND,
    TIMEOUT_2_SECONDS,
    TIMEOUT_5_SECONDS,
    APPT_TIMEZONE_SETTING_PRIMARY,
} from "../../const/constants";

const fs = require('fs');
const directoryPath = path.join(__dirname, '../../test-results/.auth');

fs.mkdir(directoryPath, (err: any) => {
  if (err) {
    console.error('error creating auth storage directory:', err);
    return
  }

  console.log('created auth storage directory');
  // when use storageState in browserstack yml, browserstack requires the file to exist already even on the
  // first time the auth-setup step is run; so must create an emtpy user.json file here
  const filepath = path.join(directoryPath, 'user.json');
  const emptyJsonObject = {};
  const jsonString = JSON.stringify(emptyJsonObject, null, 2); // The '2' adds indentation for readability
  fs.writeFileSync(filepath, jsonString);
});

// We write it here so it is blown away and re-created at the start of every test run; and is in .gitignore
const authFile = path.join(__dirname, '../../test-results/.auth/user.json');

setup('desktop browser authenticate', async ({ page }) => {
  console.log('inside authenticate setup, about to call navigate and sign in');
  // Perform authentication steps
  await navigateToAppointmentAndSignIn(page);

  // Wait until the page receives the cookies.
  // Sometimes login flow sets cookies in the process of several redirects.
  // Wait for the final URL to ensure that the cookies are actually set.
  await page.waitForURL(APPT_DASHBOARD_HOME_PAGE);
  await page.waitForTimeout(TIMEOUT_5_SECONDS);

  // ensure our settings are set to what the tests expect as default (in case a
  // previous test run failed and left the settings in an incorrect state)
  await page.goto(APPT_SETTINGS_PAGE);
  await page.waitForTimeout(TIMEOUT_5_SECONDS);
  await setDefaultUserSettingsLocalStore(page);
  await page.waitForTimeout(TIMEOUT_2_SECONDS);

  // End of authentication steps, save the auth
  await page.context().storageState({ path: authFile });

  // Now also ensure the test account is bookable (availability panel) before we start
  const availabilityPage = new AvailabilityPage(page);
  await availabilityPage.gotoAvailabilityPage();
  await availabilityPage.bookableToggleContainer.scrollIntoViewIfNeeded();
  if (! await availabilityPage.bookableToggle.isChecked()) {
    await availabilityPage.bookableToggleContainer.click();
    await page.waitForTimeout(TIMEOUT_5_SECONDS)
    console.log('turned booking availibility on');
  }

  // Ensure 'automatically confirm bookings' is turned on.
  // The section containing the auto confirm checkbox prevents playwright from being able to interact with the actual
  // checkbox element directly; we can use the checkbox element to check if it is chekced, but in order to turn it on
  // we need to then click on the checkbox container instead of the actual checkbox
  if (!await availabilityPage.autoConfirmBookingsCheckBox.isChecked()) {
    await availabilityPage.autoConfirmBookingsCheckBoxContainer.click();
    await expect(availabilityPage.autoConfirmBookingsCheckBox).toBeChecked();
  }

  // And ensure availability start time is 9am, end time 5pm
  // Sometimes it takes a couple of seconds for the start/end time values to appear
  await availabilityPage.allStartTimeInput.scrollIntoViewIfNeeded();
  await page.waitForTimeout(TIMEOUT_2_SECONDS);

  if (await availabilityPage.allStartTimeInput.inputValue() != '09:00') {
    await availabilityPage.allStartTimeInput.fill('09:00');
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    console.log('set availability start time to 09:00');
  }

  if (await availabilityPage.allEndTimeInput.inputValue() != '17:00') {
    await availabilityPage.allEndTimeInput.fill('17:00');
    await page.waitForTimeout(TIMEOUT_1_SECOND);
    console.log('set availability end time to 17:00');
  }

  // set booking meeting duration and page name
  await availabilityPage.bookingPageMtgDur30MinBtn.scrollIntoViewIfNeeded();
  await availabilityPage.bookingPageMtgDur30MinBtn.click();
  await page.waitForTimeout(TIMEOUT_1_SECOND);
  console.log('set meeting duration to 30 min');
  await availabilityPage.bookingPageNameInput.scrollIntoViewIfNeeded();
  await availabilityPage.bookingPageNameInput.fill(APPT_DISPLAY_NAME);
  await page.waitForTimeout(TIMEOUT_1_SECOND);
  await availabilityPage.bookingPageDescInput.clear();
  await page.waitForTimeout(TIMEOUT_1_SECOND);
  console.log('set booking page name and description');

  // if availability changes were made, save them
  const saveBtnVisible = await availabilityPage.saveChangesBtn.isVisible({ timeout: TIMEOUT_5_SECONDS });
  if (saveBtnVisible) {
    await availabilityPage.saveChangesBtn.click();
    await page.waitForTimeout(TIMEOUT_2_SECONDS);
    await expect(availabilityPage.savedSuccessfullyText).toBeVisible();
  }
});
