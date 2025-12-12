// utility functions that may be used by any tests
import { TBAcctsPage } from "../pages/tb-accts-page";
import { expect, type Page } from '@playwright/test';
import path from 'path';

import {
  APPT_TARGET_ENV,
  APPT_URL,
  APPT_PAGE_TITLE,
  APPT_SETTINGS_PAGE,
  APPT_DISPLAY_NAME,
  APPT_TIMEZONE_SETTING_PRIMARY,
  APPT_BROWSER_STORE_LANGUAGE_EN,
  APPT_BROWSER_STORE_THEME_LIGHT,
  APPT_BROWSER_STORE_12HR_TIME,
  APPT_BROWSER_STORE_START_WEEK_SUN,
  TIMEOUT_1_SECOND,
  TIMEOUT_2_SECONDS,
  TIMEOUT_5_SECONDS,
  TIMEOUT_60_SECONDS,
} from "../const/constants";
import { createDecipheriv } from "crypto";

const authFile = path.join(__dirname, '../test-results/.auth/user.json');


/**
 * Navigate to Appointment (at the APPT_URL in the test/e2e/.env file). If already signed in
 * then just exit; otherwise if not currently signed in then sign in using the credentials
 * provided in the .env file. When signing into Appointment on production or stage you provide
 * the TB Accounts username (email) and password; when signing in on the local dev environment
 * you provide a username (email) and password already created for your local dev stack.
 */
export const navigateToAppointmentAndSignIn = async (page: Page, testProjectName: string = 'desktop') => {
  console.log(`navigating to appointment ${APPT_TARGET_ENV} (${APPT_URL})`);   
  const tbAcctsSignInPage = new TBAcctsPage(page);
  await page.goto(`${APPT_URL}`);
  await page.waitForTimeout(TIMEOUT_5_SECONDS);

  // if we are already signed in then we can skip this
  if (await tbAcctsSignInPage.signInHeaderText.isVisible() && await tbAcctsSignInPage.signInButton.isEnabled()) {
      if (APPT_TARGET_ENV == 'prod' || APPT_TARGET_ENV == 'stage') {
          await tbAcctsSignInPage.signIn(testProjectName);
      } else {
          // local dev env doesn't use tb accts; just signs into appt using username and pword
          await tbAcctsSignInPage.localApptSignIn();
      }
  }

  // now that we're signed into the appointment dashboard give it time to load
  await expect(page).toHaveTitle(APPT_PAGE_TITLE, { timeout: TIMEOUT_60_SECONDS }); // give generous time
}

/**
 * Read and return the appointment user settings from the local browser store
 */
export const getUserSettingsFromLocalStore = async (page: Page) => {
  await page.waitForTimeout(TIMEOUT_2_SECONDS);
  const localUserStoreData = JSON.parse(await page.evaluate("localStorage.getItem('tba/user')"));
  console.log(`User settings from local browser store: ${JSON.stringify(localUserStoreData['settings'])}`);
  return localUserStoreData['settings'];
}

/**
 * Read and return the appointment user display name value from the local browser store
 */
export const getUserDisplayNameFromLocalStore = async (page: Page) => {
  const localUserStoreData = JSON.parse(await page.evaluate("localStorage.getItem('tba/user')"));
  console.log(`User display name from local browser store: ${JSON.stringify(localUserStoreData['name'])}`);
  return localUserStoreData['name'];
}

/**
 * Set the appointment user settings in the local browser store to default values required by the tests
 */
export const setDefaultUserSettingsLocalStore = async (page: Page) => {
  console.log('setting user settings to default values in browser local store')
  var localUserStoreData;

  try {
    localUserStoreData = JSON.parse(await page.evaluate("localStorage.getItem('tba/user')"));
  } catch {
    console.log('failed getting local user store, waiting and trying again');
    await page.waitForTimeout(TIMEOUT_5_SECONDS);
    localUserStoreData = JSON.parse(await page.evaluate("localStorage.getItem('tba/user')"));
  }

  console.log(`original user settings from local browser store: ${JSON.stringify(localUserStoreData['settings'])}`);

  // now set them
  localUserStoreData['name'] = APPT_DISPLAY_NAME;
  localUserStoreData['settings'] = {
      "language": APPT_BROWSER_STORE_LANGUAGE_EN,
      "colourScheme": APPT_BROWSER_STORE_THEME_LIGHT,
      "timeFormat": APPT_BROWSER_STORE_12HR_TIME,
      "timezone": APPT_TIMEZONE_SETTING_PRIMARY,
      "startOfWeek": APPT_BROWSER_STORE_START_WEEK_SUN,
  }

  await page.evaluate(`localStorage.setItem('tba/user', '${JSON.stringify(localUserStoreData)}')`);
  await page.waitForTimeout(TIMEOUT_1_SECOND);

  // get them again and verify were set
  var updatedLocalUserStoreData = JSON.parse(await page.evaluate("localStorage.getItem('tba/user')"));

  console.log(`updated user settings from local browser store: ${JSON.stringify(updatedLocalUserStoreData['settings'])}`);
  expect(updatedLocalUserStoreData['settings']).toStrictEqual(localUserStoreData['settings']);
}

/**
 * Sign into Appointment on mobile browser and set default settings required by tests
 */
export const mobileSignInAndSetup = async (page: Page, testProjectName: string) => {
  // playwright for mobile browsers doesn't support saving auth storage state, so unfortunately
  // we must sign into Appointment at the start of every test
  await navigateToAppointmentAndSignIn(page, testProjectName);
  // ensure our settings are set to what the tests expect as default (in case a
  // previous test run failed and left the settings in an incorrect state)
  await page.goto(APPT_SETTINGS_PAGE);
  await page.waitForTimeout(TIMEOUT_5_SECONDS);
  await page.waitForURL(APPT_SETTINGS_PAGE);
  await setDefaultUserSettingsLocalStore(page);
  await page.waitForTimeout(TIMEOUT_2_SECONDS);
}

/**
 * Convert an event slot date (received from the request booking page) to the date format
 * expected on the bookings list page.
 * @param dateString Date string in the format of 'February 17, 2025'
 * @returns A string containg date now formatted as MM/DD/YYYY i.e. '02/17/2025'
 */
export const convertLongDate = async (dateString: string) => {
  const date = new Date(dateString);
  const day = date.getDate();
  const month = date.getMonth() + 1; // is zero-based
  const year = date.getFullYear(); // returns a 4-digit year

  // padStart() adds a leading zero if the day or month is a single digit
  const formattedDay = String(day).padStart(2, '0');
  const formattedMonth = String(month).padStart(2, '0');
  const formattedYear = String(year);

  // return new string MM/DD/YYYY
  return `${formattedMonth}/${formattedDay}/${formattedYear}`;
}

/**
 * Ensure we are already signed into Appointment, and if we aren't then sign in. Also set
 * the default opts and save the storage and auth state. This is meant to be used at the start
 * of each test to ensure we are signed in; the auth.desktop.setup already signs us in before
 * all of the tests begin however if the tests go long the Appointment login session can expire.
 */
export const ensureWeAreSignedIn = async (page: Page) => {
  await navigateToAppointmentAndSignIn(page);
  await setDefaultUserSettingsLocalStore(page);
  await page.context().storageState({ path: authFile });
}
