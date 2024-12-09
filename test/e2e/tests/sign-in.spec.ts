import { test, expect } from '@playwright/test';
import { SplashscreenPage } from '../pages/splashscreen-page';
import { FxAPage } from '../pages/fxa-page';
import { FXA_PAGE_TITLE, APPT_PAGE_TITLE } from '../const/constants';
import { DashboardPage } from '../pages/dashboard-page';

let splashscreen: SplashscreenPage;
let fxa_sign_in: FxAPage;
let dashboard_page: DashboardPage;

test.beforeEach(async ({ page }) => {
  // navigate to the main appointment page (splashscreen)
  splashscreen = new SplashscreenPage(page);
  fxa_sign_in = new FxAPage(page);
  dashboard_page = new DashboardPage(page);
  await splashscreen.gotoProd();
});

// verify basic sign-in flow works
test.describe('basic sign-in flow', {
  tag: '@prod-sanity'
}, () => {
  test('clicking login button brings up the sign-in dialog', async ({ page }) => {
    await expect(splashscreen.loginBtn).toBeVisible();
    await splashscreen.clickLoginBtn();
    await expect(splashscreen.loginEmailInput).toBeVisible();
    await expect(splashscreen.loginContinueBtn).toBeVisible();
  });

  test('clicking continue button on login dialog brings up the fxa sign-in dialog', async ({ page }) => {
    await splashscreen.getToFxA();
    await expect(fxa_sign_in.userAvatar).toBeVisible({ timeout: 30_000}); // generous time for fxa to appear
    await expect(fxa_sign_in.signInButton).toBeVisible();
  });

  test('able to sign-in to appointment via fxa', async ({ page }) => {
    await splashscreen.getToFxA();
    await expect(fxa_sign_in.signInHeaderText).toBeVisible({ timeout: 30_000 });
    await fxa_sign_in.signIn();
    await expect(page).toHaveTitle(APPT_PAGE_TITLE, { timeout: 30_000 }); // give generous time for fxa sign to complete
    await expect(dashboard_page.userMenuAvatar).toBeVisible({ timeout: 30_000 });
    await expect(dashboard_page.navBarDashboardBtn).toBeVisible({ timeout: 30_000 });
  });
});
