#!/bin/sh
# Generate the SPA runtime config from container environment variables, and point
# the nginx API proxy at the backend.
#
# nginx:stable runs every /docker-entrypoint.d/*.sh at startup (before nginx), so
# this writes an env-specific config.js the app loads at boot. The built JS bundle
# is env-agnostic (byte-identical across environments); only this file differs.
#
# SECURITY: every value written to config.js is served publicly to browsers. Only
# map public/client-safe values into APP_* here -- never a backend secret.
#
# Values come from APP_* env (set via ExternalSecrets / ConfigMap on EKS).
set -eu

CONFIG_PATH="${APP_CONFIG_PATH:-/usr/share/nginx/html/config.js}"

# Build config.js with jq so every value is properly JSON-escaped: a value
# containing a quote, backslash, or newline cannot produce invalid JS or inject.
config_json="$(jq -n \
  --arg apiUrl "${APP_API_URL:-}" \
  --arg apiPort "${APP_API_PORT:-}" \
  --arg apiSecure "${APP_API_SECURE:-true}" \
  --arg shortBaseUrl "${APP_SHORT_BASE_URL:-}" \
  --arg authScheme "${APP_AUTH_SCHEME:-}" \
  --arg oidcRootUrl "${APP_OIDC_ROOT_URL:-}" \
  --arg oidcClientId "${APP_OIDC_CLIENT_ID:-}" \
  --arg sentryDsn "${APP_SENTRY_DSN:-}" \
  --arg posthogProjectKey "${APP_POSTHOG_PROJECT_KEY:-}" \
  --arg posthogHost "${APP_POSTHOG_HOST:-}" \
  --arg posthogUiHost "${APP_POSTHOG_UI_HOST:-}" \
  --arg tbAccountDashboardUrl "${APP_TB_ACCOUNT_DASHBOARD_URL:-}" \
  --arg tbProUrl "${APP_TB_PRO_URL:-}" \
  --arg supportUrl "${APP_SUPPORT_URL:-}" \
  --arg defaultHourFormat "${APP_DEFAULT_HOUR_FORMAT:-}" \
  '{apiUrl:$apiUrl, apiPort:$apiPort, apiSecure:$apiSecure, shortBaseUrl:$shortBaseUrl,
    authScheme:$authScheme, oidcRootUrl:$oidcRootUrl, oidcClientId:$oidcClientId,
    sentryDsn:$sentryDsn, posthogProjectKey:$posthogProjectKey, posthogHost:$posthogHost,
    posthogUiHost:$posthogUiHost, tbAccountDashboardUrl:$tbAccountDashboardUrl,
    tbProUrl:$tbProUrl, supportUrl:$supportUrl, defaultHourFormat:$defaultHourFormat}')"
printf 'window.__APP_CONFIG__ = %s;\n' "$config_json" > "$CONFIG_PATH"
echo "appointment: wrote runtime config to $CONFIG_PATH"

# Point the nginx /api proxy at the backend. On EKS the backend is a SEPARATE
# Service, so the baked default (127.0.0.1:5000, for a sidecar/dev topology) must
# be overridden. Set APP_API_UPSTREAM to host:port (no scheme), e.g.
# appointment-backend.<ns>.svc.cluster.local:5000.
if [ -n "${APP_API_UPSTREAM:-}" ]; then
  sed -i "s|127.0.0.1:5000|${APP_API_UPSTREAM}|g" /etc/nginx/conf.d/default.conf
  echo "appointment: set API upstream to ${APP_API_UPSTREAM}"
fi
