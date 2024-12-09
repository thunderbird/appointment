import { test, expect } from '@playwright/test';
import { SplashscreenPage } from '../pages/splashscreen-page';
import { FxAPage } from '../pages/fxa-page';
import { DashboardPage } from '../pages/dashboard-page';

let splashscreen: SplashscreenPage;
let fxa_sign_in: FxAPage;
let dashboard_page: DashboardPage;

test.beforeEach(async ({ page }) => {
  // navigate to the main appointment page (splashscreen) and sign-in via fxa
  splashscreen = new SplashscreenPage(page);
  fxa_sign_in = new FxAPage(page);
  dashboard_page = new DashboardPage(page);
  await splashscreen.gotoProd();
  await splashscreen.getToFxA();
  await expect(fxa_sign_in.signInHeaderText).toBeVisible({ timeout: 30_000 });
  await fxa_sign_in.signIn();
  await expect(dashboard_page.userMenuAvatar).toBeVisible({ timeout: 30_000 });
});

// verify basic sign-out flow works
test.describe('basic sign-out flow', {
  tag: '@prod-sanity'
}, () => {
  test('able to log out of appointment', async ({ page }) => {
    // todo: logout, verify back on splashscreen page
    expect(true).toBeTruthy();
  });
});
