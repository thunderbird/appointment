import { test, expect } from '@playwright/test';
import { SplashscreenPage } from '../pages/splashscreen-page';
import { APPT_PAGE_TITLE } from '../const/constants';

let splashscreenPage: SplashscreenPage;

test.beforeEach(async ({ page }) => {
  // navigate to the main appointment page (splashscreen)
  splashscreenPage = new SplashscreenPage(page);
  await splashscreenPage.gotoDashboard();
});

// verify main appointment splash screen appears correctly
test.describe('splash screen', {
  tag: ['@prod-sanity', '@e2e-suite'],
}, () => {
  test('appears correctly', async ({ page }) => {
    await expect(page).toHaveTitle(APPT_PAGE_TITLE);
    await expect(splashscreenPage.loginBtn).toBeVisible();
    await expect(splashscreenPage.signUpBetaBtn).toBeVisible();
  });
});
