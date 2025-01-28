import { test, expect } from '@playwright/test';
import { SplashscreenPage } from '../pages/splashscreen-page';
import { FxAPage } from '../pages/fxa-page';
import { APPT_PAGE_TITLE } from '../const/constants';
import { DashboardPage } from '../pages/dashboard-page';

let splashscreenPage: SplashscreenPage;
let signInPage: FxAPage;
let dashboardPage: DashboardPage;

test.beforeEach(async ({ page }) => {
  // navigate to the main appointment page (splashscreen)
  splashscreenPage = new SplashscreenPage(page);
  signInPage = new FxAPage(page);
  dashboardPage = new DashboardPage(page);
  await splashscreenPage.gotoProd();
});

// verify we are able to sign-in
test.describe('sign-in', {
  tag: '@prod-sanity'
}, () => {
  test('able to sign-in', async ({ page }) => {
    await splashscreenPage.getToFxA();

    await expect(signInPage.signInHeaderText).toBeVisible({ timeout: 30_000 }); // generous time for fxa to appear
    await expect(signInPage.userAvatar).toBeVisible({ timeout: 30_000});
    await expect(signInPage.signInButton).toBeVisible();

    await signInPage.signIn();

    await page.waitForLoadState('domcontentloaded');

    await expect(page).toHaveTitle(APPT_PAGE_TITLE, { timeout: 30_000 }); // give generous time for fxa sign-in
    await expect(dashboardPage.userMenuAvatar).toBeVisible({ timeout: 30_000 });
    await expect(dashboardPage.navBarDashboardBtn).toBeVisible({ timeout: 30_000 });
    await expect(dashboardPage.shareMyLink).toBeVisible({ timeout: 30_000 });
  });
});
