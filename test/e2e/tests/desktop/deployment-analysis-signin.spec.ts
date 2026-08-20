import { test, expect } from '@playwright/test';
import { DashboardPage } from '../../pages/dashboard-page';
import { navigateToAppointmentAndSignIn } from '../../utils/utils';

import {
  APPT_DASHBOARD_HOME_PAGE,
  PLAYWRIGHT_TAG_DEPLOYMENT_ANALYSIS,
  TIMEOUT_30_SECONDS,
  TIMEOUT_60_SECONDS,
} from '../../const/constants';

/**
 * Deployment-analysis freight-verification smoke (@deployment-analysis).
 *
 * Non-destructive OIDC sign-in check consumed by the Kargo `appointment-signin-e2e`
 * AnalysisTemplate (platform-infrastructure argocd/kargo/tb-appointment) to verify a
 * freshly-promoted tb-dev deployment. It signs in through the public tbpro Keycloak realm
 * using the EXISTING navigateToAppointmentAndSignIn helper (-> TBAcctsPage.signIn) and
 * asserts the signed-in Appointment dashboard renders.
 *
 * Deliberately SAFE to run on every freight: it performs NO booking, sends NO email, and
 * mutates NO availability/settings (it does not call setDefaultUserSettingsLocalStore, and
 * it does NOT reuse @stage-sanity, which requests a real booking and emails a bookee).
 *
 * Env consumed (all via ../../const/constants -> process.env, i.e. test/e2e .env):
 *   APPT_URL          public edge, e.g. https://appointment.tb-dev.thunderbird.dev/
 *                     (TRAILING SLASH REQUIRED -- constants build `${APPT_URL}dashboard`).
 *   APPT_TARGET_ENV   any value other than the literal `dev` (drives the OIDC sign-in path
 *                     in navigateToAppointmentAndSignIn; `dev` selects the local-password path).
 *   TB_ACCTS_EMAIL    tbpro test-user email  (TBAcctsPage.signIn).
 *   TB_ACCTS_PWORD    tbpro test-user password (TBAcctsPage.signIn).
 * It does NOT consume APPT_DISPLAY_NAME or any APPT_BOOKEE_* var.
 */
test.describe('deployment analysis sign-in smoke', () => {
  test('signs in via OIDC and the Appointment dashboard renders', {
    tag: [PLAYWRIGHT_TAG_DEPLOYMENT_ANALYSIS],
  }, async ({ page }) => {
    // Fresh context (this project loads no saved storageState): performs a real OIDC
    // sign-in through the public tbpro Keycloak. A broken sign-in throws in the helper
    // (or the title assertion within it) -> non-zero exit -> freight not marked verified.
    // navigateToAppointmentAndSignIn already asserts the page title is 'Thunderbird Appointment'.
    await navigateToAppointmentAndSignIn(page);

    // Landed on the authenticated dashboard (not bounced back to sign-in or /subscribe).
    await page.waitForURL(APPT_DASHBOARD_HOME_PAGE, { timeout: TIMEOUT_60_SECONDS });

    // Signed-in dashboard chrome renders. The Dashboard nav link is the reliable,
    // always-present signed-in element; asserting it (plus the dashboard URL above)
    // proves the dashboard rendered without a flaky testid that could wedge promotion.
    const dashboardPage = new DashboardPage(page);
    await expect(dashboardPage.navBarDashboardBtn).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
  });
});
