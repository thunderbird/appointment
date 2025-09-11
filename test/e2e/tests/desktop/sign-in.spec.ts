import { test, expect } from '@playwright/test';
import { SplashscreenPage } from '../../pages/splashscreen-page';
import { FxAPage } from '../../pages/fxa-page';
import { DashboardPage } from '../../pages/dashboard-page';
import { navigateToAppointmentAndSignIn } from '../../utils/utils';

import {
  PLAYWRIGHT_TAG_PROD_SANITY,
  TIMEOUT_30_SECONDS,
} from '../../const/constants';

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
  tag: [PLAYWRIGHT_TAG_PROD_SANITY],
}, () => {
  test('able to sign-in', async ({ page }) => {
    await navigateToAppointmentAndSignIn(page);
    await expect(dashboardPage.userMenuAvatar).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await expect(dashboardPage.navBarDashboardBtn).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
  });
});
