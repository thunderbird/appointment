#!/bin/sh
# Generate the SPA runtime config from container environment variables.
#
# The nginx:stable base image runs every /docker-entrypoint.d/*.sh at startup
# (before nginx starts), so this writes an env-specific config.js that the app
# loads at boot. The built JS bundle stays byte-identical across environments;
# only this file differs per environment.
#
# Values map from APP_* env vars (set via ExternalSecrets / ConfigMap on EKS).
set -eu

CONFIG_PATH="${APP_CONFIG_PATH:-/usr/share/nginx/html/config.js}"

cat > "$CONFIG_PATH" <<EOF
window.__APP_CONFIG__ = {
  apiUrl: "${APP_API_URL:-}",
  apiPort: "${APP_API_PORT:-}",
  apiSecure: "${APP_API_SECURE:-true}",
  shortBaseUrl: "${APP_SHORT_BASE_URL:-}",
  authScheme: "${APP_AUTH_SCHEME:-}",
  oidcRootUrl: "${APP_OIDC_ROOT_URL:-}",
  oidcClientId: "${APP_OIDC_CLIENT_ID:-}",
  sentryDsn: "${APP_SENTRY_DSN:-}",
  posthogProjectKey: "${APP_POSTHOG_PROJECT_KEY:-}",
  posthogHost: "${APP_POSTHOG_HOST:-}",
  posthogUiHost: "${APP_POSTHOG_UI_HOST:-}",
  tbAccountDashboardUrl: "${APP_TB_ACCOUNT_DASHBOARD_URL:-}",
  tbProUrl: "${APP_TB_PRO_URL:-}",
  supportUrl: "${APP_SUPPORT_URL:-}",
  defaultHourFormat: "${APP_DEFAULT_HOUR_FORMAT:-}",
};
EOF

echo "appointment: wrote runtime config to $CONFIG_PATH"
