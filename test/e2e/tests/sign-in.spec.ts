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
test.describe('basic sign-in flow', {
  tag: '@prod-sanity'
}, () => {
  test('clicking login button brings up the sign-in dialog', async ({ page }) => {
    // todo email address field, password field, and continue button are visible
    expect(true).toBeTruthy();
  });
  // todo fill out sign-in dialog etc. use the splashscreen-page object model is fine
  test('able to sign-in to appointment', async ({ page }) => {
    // todo fill out email address field, password field, and click continue button
    //      => use credentials set via local env vars (will set via secrets in CI)
    // add a splashscreen.signOut() and use that; then verify here (dashbaord appears)
    expect(true).toBeTruthy();
  });
});
