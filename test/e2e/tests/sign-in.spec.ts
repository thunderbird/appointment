import { test, expect } from '@playwright/test';
import { SplashscreenPage } from '../pages/splashscreen-page';
import { FxAPage } from '../pages/fxa-page';
import { APPT_TARGET_ENV, APPT_PAGE_TITLE, PLAYWRIGHT_TAG_PROD_SANITY, PLAYWRIGHT_TAG_E2E_SUITE, TIMEOUT_30_SECONDS } from '../const/constants';
import { DashboardPage } from '../pages/dashboard-page';

let splashscreenPage: SplashscreenPage;
let signInPage: FxAPage;
let dashboardPage: DashboardPage;

test.beforeEach(async ({ page }) => {
  // navigate to the main appointment page (splashscreen)
  splashscreenPage = new SplashscreenPage(page);
  signInPage = new FxAPage(page);
  dashboardPage = new DashboardPage(page);
  await splashscreenPage.gotoDashboard();
});

// verify we are able to sign-in
test.describe('sign-in', {
  tag: [PLAYWRIGHT_TAG_PROD_SANITY, PLAYWRIGHT_TAG_E2E_SUITE],
}, () => {
  test('able to sign-in', async ({ page }) => {
    // prod and stage use fxa to sign in; when running on local dev env we sign in to appt directly
    if (APPT_TARGET_ENV == 'prod' || APPT_TARGET_ENV == 'stage') {
      await splashscreenPage.getToFxA();
      await expect(signInPage.signInHeaderText).toBeVisible({ timeout: TIMEOUT_30_SECONDS }); // generous time for fxa to appear
      await expect(signInPage.userAvatar).toBeVisible({ timeout: TIMEOUT_30_SECONDS});
      await expect(signInPage.signInButton).toBeVisible();
      await signInPage.signIn();
    } else {
      await splashscreenPage.localApptSignIn();
    }

    await expect(page).toHaveTitle(APPT_PAGE_TITLE, { timeout: TIMEOUT_30_SECONDS }); // give generous time for sign-in
    await expect(dashboardPage.userMenuAvatar).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await expect(dashboardPage.navBarDashboardBtn).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await expect(dashboardPage.shareMyLink).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
  });
});
