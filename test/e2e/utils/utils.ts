// utility functions that may be used by any tests
import { SplashscreenPage } from "../pages/splashscreen-page";
import { FxAPage } from "../pages/fxa-page";
import { DashboardPage } from "../pages/dashboard-page";
import { expect, type Page } from '@playwright/test';
import { APPT_TARGET_ENV, APPT_URL, APPT_PAGE_TITLE } from "../const/constants";

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
        await homePage.getToFxA();
        await fxaSignInPage.signIn();
    } else {
        // local dev env doesn't use fxa; just signs into appt using username and pword
        await homePage.localApptSignIn();
    }

    // now that we're signed into the appointment dashboard give it time to load
    await page.waitForLoadState('domcontentloaded');
    await expect(page).toHaveTitle(APPT_PAGE_TITLE, { timeout: 30_000 }); // give generous time
    await expect(dashboardPage.shareMyLink).toBeVisible({ timeout: 30_000 });
}
