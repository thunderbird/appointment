// Runtime application config, loaded by index.html BEFORE the app bundle.
//
// This committed default is intentionally EMPTY: with no values set, the app
// falls back to build-time `import.meta.env.VITE_*` (your local `.env`), so the
// dev server keeps working unchanged.
//
// Per environment this file is REPLACED at deploy/run time, NOT rebuilt:
//   - S3/CloudFront: the deploy uploads an env-specific config.js to the bucket root
//   - EKS nginx:     docker-entrypoint.d/40-appointment-config.sh regenerates it from pod env
//
// The same built JS bundle is therefore byte-identical across all environments.
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
