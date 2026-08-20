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

    // The real gate: land on an AUTHENTICATED-ONLY route. A signed-in user is routed to
    // /dashboard, or to /setup when they have not completed first-time setup (a fresh user, or
    // after a tb-dev Neon branch reset). Both are auth-gated -- an unauthenticated user is
    // bounced back to sign-in and reaches neither -- so matching either proves OIDC sign-in
    // succeeded, independent of FTUE state. (Asserting a dashboard DOM element instead would
    // false-fail on /setup, where the app chrome differs; verified in-cluster with a fresh user.)
    await page.waitForURL(/\/(dashboard|setup)\/?$/, { timeout: 60_000 });
  });
});
