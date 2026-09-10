// utility functions that may be used by any tests
import { TBAcctsPage } from "../pages/tb-accts-page";
import { SettingsPage } from '../pages/settings-page';
import { expect, type Page, type Response } from '@playwright/test';
import path from 'path';

import {
  APPT_TARGET_ENV,
  APPT_URL,
  APPT_PAGE_TITLE,
  APPT_DISPLAY_NAME,
  APPT_TIMEZONE_SETTING_PRIMARY,
  APPT_BROWSER_STORE_LANGUAGE_EN,
  APPT_BROWSER_STORE_THEME_LIGHT,
  APPT_BROWSER_STORE_START_WEEK_SUN,
  TIMEOUT_1_SECOND,
  TIMEOUT_2_SECONDS,
  TIMEOUT_5_SECONDS,
  TIMEOUT_60_SECONDS,
} from "../const/constants";

const authFile = path.join(__dirname, '../test-results/.auth/user.json');

export type TestPlatform = 'desktop' | 'android' | 'ios';

/**
 * Determine the current platform from Playwright's project name.
 *
 * BrowserStack names its real-device projects `android-chrome` and
 * `ios-safari`. The local emulated mobile project is named
 * `Google-Pixel-7-View`, so Pixel and View are also treated as Android/mobile
 * indicators. All other configured project names represent desktop browsers.
 *
 * Keep passing the original project name to page objects and sign-in helpers;
 * they use the exact name for their own targeted platform workarounds. This
 * utility provides the broader platform category used by shared test flows.
 */
export const getTestPlatform = (projectName: string): TestPlatform => {
  const normalizedProjectName = projectName.toLowerCase();

  if (normalizedProjectName.includes('ios') || normalizedProjectName.includes('iphone')) {
    return 'ios';
  }

  if (
    normalizedProjectName.includes('android') ||
    normalizedProjectName.includes('pixel') ||
    normalizedProjectName.includes('view')
  ) {
    return 'android';
  }

  return 'desktop';
};


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
  type SignInState = 'authenticated' | 'local-sign-in' | 'oidc-sign-in' | 'loading';

  let profileLoadedSuccessfully = false;

  // The dashboard validates the access token by loading the user's profile.
  // Start observing before navigation so a fast response cannot be missed.
  const trackProfileResponse = (response: Response) => {
    const isProfileRequest = (
      response.request().method() === 'GET' &&
      new URL(response.url()).pathname.endsWith('/me')
    );

    if (isProfileRequest && response.ok()) {
      profileLoadedSuccessfully = true;
    }
  };

  page.on('response', trackProfileResponse);
  await page.goto(`${APPT_URL}`);

  const getSignInState = async (): Promise<SignInState> => {
    // A successful profile response proves that the backend accepted the
    // current access token. URL or title alone can reflect stale client state.
    if (profileLoadedSuccessfully) {
      return 'authenticated';
    }

    if (APPT_TARGET_ENV == 'dev' && await tbAcctsSignInPage.localDevEmailInput.isVisible()) {
      return 'local-sign-in';
    }

    if (await tbAcctsSignInPage.signInHeaderText.isVisible()) {
      return 'oidc-sign-in';
    }

    return 'loading';
  };

  const completeSignInIfRequired = async () => {
    // Expired sessions can pass through several Appointment and Keycloak
    // redirects before a login form is rendered. Poll the actual auth state so
    // a slow redirect cannot make the helper skip the required sign-in.
    await expect
      .poll(getSignInState, {
        timeout: TIMEOUT_60_SECONDS,
        message: 'Waiting for an authenticated Appointment session or a sign-in form',
      })
      .not.toBe('loading');

    const signInState = await getSignInState();

    // Local dev can use password-only auth or OIDC, depending on configuration.
    if (signInState === 'local-sign-in') {
      await tbAcctsSignInPage.localApptSignIn();
    } else if (signInState === 'oidc-sign-in') {
      await tbAcctsSignInPage.signIn(testProjectName);
    }

    // If a login was required, wait for its profile request to prove that the
    // replacement token was accepted before allowing another navigation.
    await expect
      .poll(() => profileLoadedSuccessfully, {
        timeout: TIMEOUT_60_SECONDS,
        message: 'Waiting for Appointment to validate the signed-in user profile',
      })
      .toBeTruthy();
  };

  await completeSignInIfRequired();

  // A token can still be valid during beforeEach but expire midway through a
  // stateful settings test. Decode only its expiry inside the browser and
  // refresh proactively when less than two minutes remain. Opaque/non-JWT
  // tokens return null and continue to use backend profile validation alone.
  const accessTokenSecondsRemaining = await page.evaluate(() => {
    try {
      const storedUser = JSON.parse(window.localStorage.getItem('tba/user') ?? 'null');
      const accessToken = storedUser?.accessToken;
      const encodedPayload = accessToken?.split('.')[1];

      if (!encodedPayload) {
        return null;
      }

      const base64Payload = encodedPayload
        .replace(/-/g, '+')
        .replace(/_/g, '/')
        .padEnd(Math.ceil(encodedPayload.length / 4) * 4, '=');
      const expiresAt = JSON.parse(window.atob(base64Payload))?.exp;

      return typeof expiresAt === 'number' ? expiresAt - Date.now() / 1000 : null;
    } catch {
      return null;
    }
  });

  if (accessTokenSecondsRemaining !== null && accessTokenSecondsRemaining < 120) {
    console.log('Appointment access token is close to expiry; refreshing the sign-in session');
    profileLoadedSuccessfully = false;

    // Removing only Appointment's client-side user record makes the root route
    // start the configured login flow. An active OIDC SSO cookie may complete
    // it automatically; otherwise the helper waits for and fills the form.
    await page.evaluate(() => window.localStorage.removeItem('tba/user'));
    await page.goto(`${APPT_URL}`);
    await completeSignInIfRequired();
  }

  // The successful profile response above is the authoritative authentication
  // check. Do not additionally wait for a specific client-side route here:
  // BrowserStack iOS can continue reporting the transient post-login URL even
  // after Appointment has rendered the authenticated UI. Each caller performs
  // an explicit page.goto() to the page it needs immediately after this helper.
  await expect(page).toHaveTitle(/Appointment/i, { timeout: TIMEOUT_60_SECONDS });
  page.off('response', trackProfileResponse);
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
 * Set the appointment user settings in the local browser store to default values required by the tests.
 * If setTimeZone is provided set the Appointment app default timezone setting to that value, otherwise use
 * APPT_TIMEZONE_SETTING_PRIMARY. This allows the book an appoitment test to set the timezone in Appointment
 * to the timezone that was used by the booking page, when a timeslot was selected.
 */
export const setDefaultUserSettingsLocalStore = async (page: Page, setTimeZone: string = APPT_TIMEZONE_SETTING_PRIMARY) => {
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

  // if setTimeZone is 'UTC' use 'Europe/Dublin'
  if (setTimeZone == 'UTC')
     setTimeZone = 'Europe/Dublin';

  // now set them
  localUserStoreData['name'] = APPT_DISPLAY_NAME;
  localUserStoreData['settings'] = {
      "language": APPT_BROWSER_STORE_LANGUAGE_EN,
      "colourScheme": APPT_BROWSER_STORE_THEME_LIGHT,
      "timezone": setTimeZone,
      "startOfWeek": APPT_BROWSER_STORE_START_WEEK_SUN,
  }

  console.log(`setting user settings in local browser store to: ${JSON.stringify(localUserStoreData['settings'])}`);
  await page.evaluate(`localStorage.setItem('tba/user', '${JSON.stringify(localUserStoreData)}')`);
  await page.waitForTimeout(TIMEOUT_1_SECOND);

  // get them again and verify were set
  var updatedLocalUserStoreData = JSON.parse(await page.evaluate("localStorage.getItem('tba/user')"));
  console.log(`user settings from local browser store are now: ${JSON.stringify(updatedLocalUserStoreData['settings'])}`);
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
  const settingsPage = new SettingsPage(page);
  await settingsPage.gotoAccountSettings();
  await page.waitForTimeout(TIMEOUT_5_SECONDS);
  await setDefaultUserSettingsLocalStore(page);
  await page.waitForTimeout(TIMEOUT_2_SECONDS);
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
