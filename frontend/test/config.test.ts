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
});
