import { test, expect } from '@playwright/test';
import { SplashscreenPage } from '../pages/splashscreen-page';
import { APPT_PAGE_TITLE } from '../const/constants';

let splashscreen: SplashscreenPage;

test.beforeEach(async ({ page }) => {
  // navigate to the main appointment page (splashscreen)
  splashscreen = new SplashscreenPage(page);
  await splashscreen.gotoProd();
});

// verify main appointment splash screen appears correctly
test.describe('splash screen', {
  tag: '@prod-sanity'
}, () => {
  test('appears correctly', async ({ page }) => {
    await expect(page).toHaveTitle(APPT_PAGE_TITLE);
    await expect(splashscreen.loginBtn).toBeVisible();
    await expect(splashscreen.signUpBetaBtn).toBeVisible();
  });
});
