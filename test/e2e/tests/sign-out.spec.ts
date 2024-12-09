import { test, expect } from '@playwright/test';
import { SplashscreenPage } from '../pages/splashscreen-page';
import { APPT_PAGE_TITLE } from '../const/constants';

let splashscreen: SplashscreenPage;

test.beforeEach(async ({ page }) => {
  // navigate to the main appointment page (splashscreen)
  splashscreen = new SplashscreenPage(page);
  await splashscreen.gotoProd();
  // todo fill out email address field, password field, and click continue button
  //      => use credentials set via local env vars (will set via secrets in CI)
  // then verifiy sign-in was successful - dashboard appears
  // use splashscreen-page signOn() method
});

// verify main appointment splash screen appears correctly
test.describe('basic sign-out flow', {
  tag: '@prod-sanity'
}, () => {
  test('able to sign-out of appointment', async ({ page }) => {
    // todo sign out and verify splashscreen appears with login button visible
    expect(true).toBeTruthy();
  });
});
