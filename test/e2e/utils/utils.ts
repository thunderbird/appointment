// utility functions that may be used by any tests
import { SplashscreenPage } from "../pages/splashscreen-page";
import { FxAPage } from "../pages/fxa-page";
import { expect, type Page } from '@playwright/test';

import {
    APPT_TARGET_ENV,
    APPT_URL,
    APPT_PAGE_TITLE,
    APPT_DASHBOARD_HOME_PAGE,
    APPT_SETTINGS_PAGE,
    APPT_DISPLAY_NAME,
    APPT_TIMEZONE_SETTING_PRIMARY,
    APPT_BROWSER_STORE_LANGUAGE_EN,
    APPT_BROWSER_STORE_THEME_LIGHT,
    APPT_BROWSER_STORE_12HR_TIME,
    APPT_BROWSER_STORE_START_WEEK_SUN,
    TIMEOUT_1_SECOND,
    TIMEOUT_2_SECONDS,
    TIMEOUT_3_SECONDS,
    TIMEOUT_60_SECONDS,
} from "../const/constants";

/**
 * Navigate to and sign into the Appointment application target environment, using the URL and
 * credentials provided in the .env file. When signing into Appointment on production or stage
 * you provide the username (email) and then are redirected to the FxA sign in page. When signing
 * in on the local dev environment you provide a username (email) and password directly and are
 * not redirected to sign in to FxA.
 */
export const navigateToAppointmentAndSignIn = async (page: Page) => {
    console.log(`navigating to appointment ${APPT_TARGET_ENV} (${APPT_URL}) and signing in`);
    const homePage = new SplashscreenPage(page);
    const fxaSignInPage = new FxAPage(page);

    await homePage.gotoDashboard();

    if (APPT_TARGET_ENV == 'prod' || APPT_TARGET_ENV == 'stage') {
        // check for the 'continue' button first in case sign-in was saved in local cookies
        if (await homePage.homeContinueBtn.isVisible() &&  await homePage.homeContinueBtn.isEnabled()) {
            console.log("already signed in; just need to click the Appointment home page 'continue' button");
            await homePage.homeContinueBtn.click();
            await page.waitForTimeout(TIMEOUT_3_SECONDS);
        } else {
            await homePage.getToFxA();
            await fxaSignInPage.signIn();
        }
    } else {
        // local dev env doesn't use fxa; just signs into appt using username and pword
        await homePage.localApptSignIn();
    }

    // now that we're signed into the appointment dashboard give it time to load
    await expect(page).toHaveTitle(APPT_PAGE_TITLE, { timeout: TIMEOUT_60_SECONDS }); // give generous time
}

/**
 * Read and return the appointment user settings from the local browser store
 */
export const getUserSettingsFromLocalStore = async (page: Page) => {
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
    var localUserStoreData = JSON.parse(await page.evaluate("localStorage.getItem('tba/user')"));

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
export const mobileSignInAndSetup = async (page: Page) => {
    // playwright for mobile browsers doesn't support saving auth storage state, so unfortunately
    // we must sign into Appointment at the start of every test
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
}
