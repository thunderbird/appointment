// Runtime application configuration.
//
// Config is read at runtime from `window.__APP_CONFIG__`, injected by `/config.js`
// (loaded synchronously in index.html BEFORE the app bundle), with FALLBACK to
// build-time `import.meta.env.VITE_*`.
//
//   - EKS / container path: the nginx entrypoint regenerates config.js from APP_*
//     pod env, and the image is built env-agnostic (no baked values) -> config.js
//     is the ONLY source and MUST be present (see assertConfigured, called at boot).
//     Only this bundle is byte-identical across environments.
//   - Existing S3/CloudFront path (workflows unchanged): the build still bakes
//     VITE_* via `--mode`; the committed EMPTY public/config.js falls through to
//     those baked values, so behavior is identical to before (backwards compatible).
//   - Local dev / unit tests: fall back to `.env` via import.meta.env.
//
// NOTE: pick()'s "empty string = unset" rule means the container build must stay
// env-agnostic; a reintroduced baked `.env`/`--mode` there would let a
// runtime-empty value silently fall back to the baked one.
//
// Design (in platform-infrastructure): docs/superpowers/specs/2026-07-20-appointment-eks-kargo-promotion-pipeline-design.md (§C)

export type AppConfig = {
  apiUrl?: string;
  apiPort?: string;
  apiSecure?: string;
  shortBaseUrl?: string;
  authScheme?: string;
  oidcRootUrl?: string;
  oidcClientId?: string;
  sentryDsn?: string;
  posthogProjectKey?: string;
  posthogHost?: string;
  posthogUiHost?: string;
  tbAccountDashboardUrl?: string;
  tbProUrl?: string;
  supportUrl?: string;
  defaultHourFormat?: string;
};

declare global {
  interface Window {
    __APP_CONFIG__?: AppConfig;
  }
}

const runtime = (): AppConfig =>
  (typeof window !== 'undefined' && window.__APP_CONFIG__) || {};

// Prefer a non-empty runtime value; otherwise fall back to the build-time Vite env
// (used in dev and unit tests). An empty string is treated as "unset".
const pick = (runtimeVal: string | undefined, envVal: string | undefined): string | undefined =>
  runtimeVal !== undefined && runtimeVal !== '' ? runtimeVal : envVal;

const env = (import.meta.env ?? {}) as Record<string, string | undefined>;

/**
 * Runtime config accessor. Each getter resolves at call time, so it reflects
 * whatever `/config.js` injected before the bundle loaded.
 */
export const config = {
  get apiUrl() {
    return pick(runtime().apiUrl, env.VITE_API_URL);
  },
  get apiPort() {
    return pick(runtime().apiPort, env.VITE_API_PORT);
  },
  get apiSecure() {
    return pick(runtime().apiSecure, env.VITE_API_SECURE);
  },
  get shortBaseUrl() {
    return pick(runtime().shortBaseUrl, env.VITE_SHORT_BASE_URL);
  },
  get authScheme() {
    return pick(runtime().authScheme, env.VITE_AUTH_SCHEME);
  },
  get oidcRootUrl() {
    return pick(runtime().oidcRootUrl, env.VITE_OIDC_ROOT_URL);
  },
  get oidcClientId() {
    return pick(runtime().oidcClientId, env.VITE_OIDC_CLIENT_ID);
  },
  get sentryDsn() {
    return pick(runtime().sentryDsn, env.VITE_SENTRY_DSN);
  },
  get posthogProjectKey() {
    return pick(runtime().posthogProjectKey, env.VITE_POSTHOG_PROJECT_KEY);
  },
  get posthogHost() {
    return pick(runtime().posthogHost, env.VITE_POSTHOG_HOST);
  },
  get posthogUiHost() {
    return pick(runtime().posthogUiHost, env.VITE_POSTHOG_UI_HOST);
  },
  get tbAccountDashboardUrl() {
    return pick(runtime().tbAccountDashboardUrl, env.VITE_TB_ACCOUNT_DASHBOARD_URL);
  },
  get tbProUrl() {
    return pick(runtime().tbProUrl, env.VITE_TB_PRO_URL);
  },
  get supportUrl() {
    return pick(runtime().supportUrl, env.VITE_SUPPORT_URL);
  },
  get defaultHourFormat() {
    return pick(runtime().defaultHourFormat, env.VITE_DEFAULT_HOUR_FORMAT);
  },
};

/**
 * Fail loud if the app is unconfigured. On the container/EKS path there is no
 * baked fallback, so a missing or empty `/config.js` (e.g. the entrypoint didn't
 * run, or `APP_API_URL` was unset) would otherwise boot a silently-broken app.
 * Call once at startup (main.ts). Dev/tests and the existing S3 build resolve
 * `apiUrl` via `.env`/`--mode` fallback, so this only throws when truly unset.
 */
export const assertConfigured = (): void => {
  if (!config.apiUrl) {
    console.error(
      '[config] window.__APP_CONFIG__ is missing/empty (no /config.js?). The SPA is unconfigured.'
    );
    throw new Error('Appointment SPA is unconfigured: config.apiUrl is empty (check /config.js).');
  }
};

export default config;
