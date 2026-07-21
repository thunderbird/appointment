// Runtime application config, loaded by index.html BEFORE the app bundle.
//
// SECURITY: every value here is served publicly to browsers. Never put a secret
// in this file (or in the APP_* vars the container entrypoint reads).
//
// This committed default is intentionally EMPTY: with no values set, the app
// falls back to build-time `import.meta.env.VITE_*`, so local dev (your `.env`)
// and the existing S3/CloudFront deploy (which still bakes VITE_* via `--mode`)
// keep working unchanged.
//
// On the EKS / container path only, this file is REGENERATED at container start
// from APP_* pod env by docker-entrypoint.d/40-appointment-config.sh. That
// container bundle is env-agnostic (byte-identical across environments); the S3
// bundle is still built per-environment with `--mode`.
window.__APP_CONFIG__ = {
  apiUrl: '',
  apiPort: '',
  apiSecure: '',
  shortBaseUrl: '',
  authScheme: '',
  oidcRootUrl: '',
  oidcClientId: '',
  sentryDsn: '',
  posthogProjectKey: '',
  posthogHost: '',
  posthogUiHost: '',
  tbAccountDashboardUrl: '',
  tbProUrl: '',
  supportUrl: '',
  defaultHourFormat: '',
};
