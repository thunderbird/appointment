import { test, expect } from '@playwright/test';
import { navigateToAppointmentAndSignIn } from '../../utils/utils';
import { PLAYWRIGHT_TAG_DEPLOYMENT_ANALYSIS } from '../../const/constants';

/**
 * Deployment-analysis freight-verification smoke (@deployment-analysis).
 *
 * Non-destructive OIDC sign-in check consumed by the Kargo `appointment-signin-e2e`
 * AnalysisTemplate (platform-infrastructure#1046): it clones this repo at main and runs
 * `deployment-analysis-e2e` against a freshly-promoted tb-dev deployment. A red run means
 * the freight is not marked verified.
 *
 * SAFE to run on every freight: sign-in only -- no booking, no email, no availability/
 * settings mutation (it does not use auth.desktop.setup or @stage-sanity).
 *
 * Env consumed (via ../../const/constants -> process.env, i.e. test/e2e .env):
 *   APPT_URL          public edge, e.g. https://appointment.tb-dev.thunderbird.dev/ (trailing slash).
 *   APPT_TARGET_ENV   any value other than the literal `dev` (drives the OIDC path).
 *   TB_ACCTS_EMAIL / TB_ACCTS_PWORD   tbpro test-user creds (TBAcctsPage.signIn).
 */
test.describe('deployment analysis sign-in smoke', () => {
  test('signs in via OIDC and the authenticated app renders', {
    tag: [PLAYWRIGHT_TAG_DEPLOYMENT_ANALYSIS],
  }, async ({ page }) => {
    // Fail LOUD and immediately if the gate is misconfigured, rather than signing in as
    // nobody and timing out 60s later (which reads like a broken deploy, not a config error).
    for (const key of ['APPT_URL', 'TB_ACCTS_EMAIL', 'TB_ACCTS_PWORD']) {
      expect(process.env[key], `${key} must be set for the deployment-analysis smoke`).toBeTruthy();
    }

    // Real OIDC sign-in through the public tbpro Keycloak. The helper asserts the app title,
    // but that title is also present on the signed-OUT app, so it is NOT sufficient on its own.
    await navigateToAppointmentAndSignIn(page);

    // The real gate: an element that ONLY renders for an authenticated subscriber. The desktop
    // NavBar (`.nav-items-container`, NavBar.vue) is present only when user.authenticated, on
    // BOTH /dashboard and the first-time-user /setup redirect, so this proves sign-in succeeded
    // without conflating it with FTUE-complete. Scoped to the nav container so it resolves to a
    // single element (a page-wide getByRole('link',{name:'Dashboard'}) also matches the footer).
    const navDashboardLink = page.locator('.nav-items-container').getByRole('link', { name: 'Dashboard' });
    await expect(navDashboardLink).toBeVisible({ timeout: 60_000 });
  });
});
