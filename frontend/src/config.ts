// Runtime application configuration.
//
// Config is read at runtime from `window.__APP_CONFIG__`, which is injected by
// `/config.js` (loaded synchronously in index.html BEFORE the app bundle). This
// lets a single built bundle run unchanged in every environment:
//
//   - existing S3/CloudFront envs: the deploy uploads an env-specific config.js
//   - EKS nginx container:         the entrypoint generates config.js from pod env
//
// For local dev and unit tests (no config.js present) we fall back to Vite's
// build-time `import.meta.env.VITE_*`, so existing `.env` workflows keep working.
//
// See docs: docs/superpowers/specs/2026-07-20-appointment-eks-kargo-promotion-pipeline-design.md (§C)

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

export default config;
