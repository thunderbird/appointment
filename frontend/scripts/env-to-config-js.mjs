// Generate dist/config.js from a dotenv file's VITE_* values, for the existing
// S3/CloudFront deploy. This is the backwards-compatible bridge to runtime config:
// the built bundle reads window.__APP_CONFIG__ from /config.js, and here we produce
// that file from the SAME .env values that `--mode <env>` bakes as the fallback — so
// runtime behavior is identical to before, but now driven by config.js.
//
// Usage: node scripts/env-to-config-js.mjs <envFile> [outFile]
//   node scripts/env-to-config-js.mjs .env.stage dist/config.js
//
// The container path (EKS) uses docker/docker-entrypoint.d/40-appointment-config.sh
// instead, generating config.js from APP_* pod env. Both produce the same shape.
import { readFileSync, writeFileSync } from 'node:fs';
import process from 'node:process';

const envFile = process.argv[2];
const outFile = process.argv[3] ?? 'dist/config.js';

if (!envFile) {
  console.error('usage: node scripts/env-to-config-js.mjs <envFile> [outFile]');
  process.exit(1);
}

// Minimal dotenv parser: KEY=VALUE lines, ignoring comments/blanks, stripping quotes.
const parseEnv = (path) => {
  const map = {};
  for (const line of readFileSync(path, 'utf8').split('\n')) {
    const m = line.match(/^\s*([A-Za-z0-9_]+)\s*=\s*(.*?)\s*$/);
    if (!m) continue;
    map[m[1]] = m[2].replace(/^["']|["']$/g, '');
  }
  return map;
};

const e = parseEnv(envFile);

// Must mirror the AppConfig keys read by src/config.ts.
const appConfig = {
  apiUrl: e.VITE_API_URL ?? '',
  apiPort: e.VITE_API_PORT ?? '',
  apiSecure: e.VITE_API_SECURE ?? '',
  shortBaseUrl: e.VITE_SHORT_BASE_URL ?? '',
  authScheme: e.VITE_AUTH_SCHEME ?? '',
  oidcRootUrl: e.VITE_OIDC_ROOT_URL ?? '',
  oidcClientId: e.VITE_OIDC_CLIENT_ID ?? '',
  sentryDsn: e.VITE_SENTRY_DSN ?? '',
  posthogProjectKey: e.VITE_POSTHOG_PROJECT_KEY ?? '',
  posthogHost: e.VITE_POSTHOG_HOST ?? '',
  posthogUiHost: e.VITE_POSTHOG_UI_HOST ?? '',
  tbAccountDashboardUrl: e.VITE_TB_ACCOUNT_DASHBOARD_URL ?? '',
  tbProUrl: e.VITE_TB_PRO_URL ?? '',
  supportUrl: e.VITE_SUPPORT_URL ?? '',
  defaultHourFormat: e.VITE_DEFAULT_HOUR_FORMAT ?? '',
};

writeFileSync(outFile, `window.__APP_CONFIG__ = ${JSON.stringify(appConfig, null, 2)};\n`);
console.log(`env-to-config-js: wrote ${outFile} from ${envFile}`);
