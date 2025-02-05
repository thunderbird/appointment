// utility functions that may be used by any tests
import { SplashscreenPage } from "../pages/splashscreen-page";
import { FxAPage } from "../pages/fxa-page";
import { DashboardPage } from "../pages/dashboard-page";
import { expect, type Page } from '@playwright/test';
import { APPT_URL, APPT_PAGE_TITLE } from "../const/constants";

/**
 * Navigate to and sign into the Appointment application using the production URL and
 * production credentials provided in the .env file.
 */
export const navigateToAppointmentProdAndSignIn = async (page: Page) => {
    console.log(`navigating to appointment production (${APPT_URL}) and signing in`);
    const homePage = new SplashscreenPage(page);
    const signInPage = new FxAPage(page);
    const dashboardPage = new DashboardPage(page);
    await homePage.gotoProd();
    await homePage.getToFxA();
    await signInPage.signIn();
    // now that we're signed into the appointment dashboard give it time to load
    await page.waitForLoadState('domcontentloaded');
    await expect(page).toHaveTitle(APPT_PAGE_TITLE, { timeout: 30_000 }); // give generous time
    await expect(dashboardPage.shareMyLink).toBeVisible({ timeout: 30_000 });
}
