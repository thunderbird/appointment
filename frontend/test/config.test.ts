import {
  describe, it, expect, afterEach,
} from 'vitest';
import { config } from '@/config';

describe('runtime config accessor', () => {
  afterEach(() => {
    delete window.__APP_CONFIG__;
  });

  it('prefers window.__APP_CONFIG__ when a value is present', () => {
    window.__APP_CONFIG__ = { apiUrl: 'runtime.example.test', authScheme: 'oidc' };
    expect(config.apiUrl).toBe('runtime.example.test');
    expect(config.authScheme).toBe('oidc');
  });

  it('falls back to build-time import.meta.env when the runtime value is absent', () => {
    delete window.__APP_CONFIG__;
    expect(config.apiUrl).toBe(import.meta.env.VITE_API_URL);
  });

  it('treats an empty runtime string as unset and falls back', () => {
    window.__APP_CONFIG__ = { apiUrl: '' };
    expect(config.apiUrl).toBe(import.meta.env.VITE_API_URL);
  });

  it('resolves getters at call time (reflects a later window mutation)', () => {
    delete window.__APP_CONFIG__;
    expect(config.tbProUrl).toBe(import.meta.env.VITE_TB_PRO_URL);
    window.__APP_CONFIG__ = { tbProUrl: 'https://pro.example.test' };
    expect(config.tbProUrl).toBe('https://pro.example.test');
  });

  // Guard the 15 near-identical getters against copy-paste/rebase errors: each key
  // must prefer its runtime value AND fall back to its OWN VITE_ env var.
  const KEYS: Array<[keyof typeof config, string]> = [
    ['apiUrl', 'VITE_API_URL'],
    ['apiPort', 'VITE_API_PORT'],
    ['apiSecure', 'VITE_API_SECURE'],
    ['shortBaseUrl', 'VITE_SHORT_BASE_URL'],
    ['authScheme', 'VITE_AUTH_SCHEME'],
    ['oidcRootUrl', 'VITE_OIDC_ROOT_URL'],
    ['oidcClientId', 'VITE_OIDC_CLIENT_ID'],
    ['sentryDsn', 'VITE_SENTRY_DSN'],
    ['posthogProjectKey', 'VITE_POSTHOG_PROJECT_KEY'],
    ['posthogHost', 'VITE_POSTHOG_HOST'],
    ['posthogUiHost', 'VITE_POSTHOG_UI_HOST'],
    ['tbAccountDashboardUrl', 'VITE_TB_ACCOUNT_DASHBOARD_URL'],
    ['tbProUrl', 'VITE_TB_PRO_URL'],
    ['supportUrl', 'VITE_SUPPORT_URL'],
    ['defaultHourFormat', 'VITE_DEFAULT_HOUR_FORMAT'],
  ];

  it.each(KEYS)('runtime value wins for %s', (key) => {
    window.__APP_CONFIG__ = { [key]: `rt-${key}` };
    expect(config[key]).toBe(`rt-${key}`);
  });

  it.each(KEYS)('%s falls back to its own env var when runtime is unset', (key, envVar) => {
    delete window.__APP_CONFIG__;
    expect(config[key]).toBe((import.meta.env as Record<string, string | undefined>)[envVar]);
  });

  it('a partial runtime object still falls back per-key for unset keys', () => {
    window.__APP_CONFIG__ = { tbProUrl: 'https://pro.example.test' };
    expect(config.tbProUrl).toBe('https://pro.example.test');
    expect(config.apiUrl).toBe(import.meta.env.VITE_API_URL);
  });
});
