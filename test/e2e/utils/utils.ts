// utility functions that may be used by any tests
import { SplashscreenPage } from "../pages/splashscreen-page";
import { FxAPage } from "../pages/fxa-page";
import { DashboardPage } from "../pages/dashboard-page";
import { expect, type Page } from '@playwright/test';

import {
    APPT_TARGET_ENV,
    APPT_URL,
    APPT_PAGE_TITLE,
    TIMEOUT_1_SECOND,
    APPT_DISPLAY_NAME,
    APPT_BROWSER_STORE_LANGUAGE_EN,
    APPT_BROWSER_STORE_THEME_LIGHT,
    APPT_BROWSER_STORE_12HR_TIME,
    APPT_TIMEZONE_SETTING_TORONTO,
    APPT_BROWSER_STORE_START_WEEK_SUN,
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
    const dashboardPage = new DashboardPage(page);

    await homePage.gotoDashboard();

    if (APPT_TARGET_ENV == 'prod' || APPT_TARGET_ENV == 'stage') {
        // when running on mobile on BrowserStack the cookies are saved for the entire session, so if a previous
        // test ran in the same session then the browser is already be signed in; in which case just the Appointment
        // 'continue' button may be displayed instead of the 'log in' button. Check for the 'continue' button first
        // and if it's there we can just click that and be signed in, and skip the rest
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

        // when running in CI on a PR the appt stack is started fresh each time; so the FTUE will appear
        // go through the first time user setup so that the appt acct is ready before heading to dashboard
        const on_create_profile = await homePage.createProfileHeader.isVisible();
        if (on_create_profile) {
            await homePage.firstTimeUserSetup();
        }
    }

    // now that we're signed into the appointment dashboard give it time to load
    await expect(page).toHaveTitle(APPT_PAGE_TITLE, { timeout: TIMEOUT_60_SECONDS }); // give generous time
    await expect(dashboardPage.shareMyLink).toBeVisible({ timeout: TIMEOUT_60_SECONDS });
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
        "timezone": APPT_TIMEZONE_SETTING_TORONTO,
        "startOfWeek": APPT_BROWSER_STORE_START_WEEK_SUN,
    }

    await page.evaluate(`localStorage.setItem('tba/user', '${JSON.stringify(localUserStoreData)}')`);
    await page.waitForTimeout(TIMEOUT_1_SECOND);

    // get them again and verify were set
    var updatedLocalUserStoreData = JSON.parse(await page.evaluate("localStorage.getItem('tba/user')"));

    console.log(`updated user settings from local browser store: ${JSON.stringify(updatedLocalUserStoreData['settings'])}`);
    expect(updatedLocalUserStoreData['settings']).toStrictEqual(localUserStoreData['settings']);
}
