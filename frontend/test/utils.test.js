import { describe, it, expect, afterEach } from 'vitest';
import { timeFormat } from '@/utils';

// Mock the browser locale with setting window.navigator.language directly.
const setLocale = (locale) => {
  Object.defineProperty(window.navigator, 'language', { value: locale, configurable: true });
};

describe('timeFormat', () => {
  afterEach(() => {
    setLocale('en-US');
    delete window.__APP_CONFIG__;
  });

  it('detects a 12-hour format for a 12-hour locale (en-US)', () => {
    setLocale('en-US');
    expect(timeFormat()).toBe('hh:mma');
  });

  it('detects a 24-hour format for a 24-hour locale (de-DE)', () => {
    setLocale('de-DE');
    expect(timeFormat()).toBe('HH:mm');
  });

  it('detects a 24-hour format for en-GB, which uses 24-hour time despite being English', () => {
    setLocale('en-GB');
    expect(timeFormat()).toBe('HH:mm');
  });

  it('falls back to the configured default when the locale is invalid', () => {
    setLocale('not-a-real-locale!!');
    window.__APP_CONFIG__ = { defaultHourFormat: '24' };
    expect(timeFormat()).toBe('HH:mm');
  });

  it('falls back to 12-hour format when the locale is invalid and no default is configured', () => {
    setLocale('not-a-real-locale!!');
    expect(timeFormat()).toBe('hh:mma');
  });
});
