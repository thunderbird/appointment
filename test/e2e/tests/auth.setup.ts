import { test as setup } from '@playwright/test';
import path from 'path';

import { navigateToAppointmentAndSignIn, setDefaultUserSettingsLocalStore } from '../utils/utils';

import {
    APPT_DASHBOARD_HOME_PAGE,
    APPT_SETTINGS_PAGE,
    TIMEOUT_2_SECONDS,
} from "../const/constants";

const fs = require('fs');
const directoryPath = path.join(__dirname, '../test-results/.auth');

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
const authFile = path.join(__dirname, '../test-results/.auth/user.json');

setup('authenticate', async ({ page }) => {
  console.log('inside authenticate setup, about to call navigate and sign in');
  // Perform authentication steps
  await navigateToAppointmentAndSignIn(page);

  // Wait until the page receives the cookies.
  // Sometimes login flow sets cookies in the process of several redirects.
  // Wait for the final URL to ensure that the cookies are actually set.
  await page.waitForURL(APPT_DASHBOARD_HOME_PAGE);
  await page.waitForTimeout(TIMEOUT_2_SECONDS);

  // ensure our settings are set to what the tests expect as default (in case a
  // previous test run failed and left the settings in an incorrect state)
  await page.goto(APPT_SETTINGS_PAGE);
  await page.waitForTimeout(TIMEOUT_2_SECONDS);
  await setDefaultUserSettingsLocalStore(page);
  await page.waitForTimeout(TIMEOUT_2_SECONDS);

  // End of authentication steps.
  await page.context().storageState({ path: authFile });
});
