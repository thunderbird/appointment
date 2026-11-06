import { describe, it, expect, afterEach } from 'vitest';
import { assignEventLanes, timeFormat } from '@/utils';

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

describe('assignEventLanes', () => {
  // Build an event from hours, e.g. ev(11.5, 13) is 11:30 - 13:00
  const ev = (start, end) => ({ start: start * 3600000, end: end * 3600000 });

  it('keeps non-overlapping events at full width', () => {
    expect(assignEventLanes([ev(9, 10), ev(11, 12)])).toEqual([
      { currentLane: 0, totalLanes: 1 },
      { currentLane: 0, totalLanes: 1 },
    ]);
  });

  it('does not treat back-to-back events as overlapping', () => {
    expect(assignEventLanes([ev(9, 9.5), ev(9.5, 10)])).toEqual([
      { currentLane: 0, totalLanes: 1 },
      { currentLane: 0, totalLanes: 1 },
    ]);
  });

  it('reuses a free lane within an overlap cluster', () => {
    expect(assignEventLanes([ev(11.5, 13), ev(12, 14), ev(13, 14.5)])).toEqual([
      { currentLane: 0, totalLanes: 2 },
      { currentLane: 1, totalLanes: 2 },
      { currentLane: 0, totalLanes: 2 },
    ]);
  });

  it('opens a lane per concurrent event and starts a new cluster afterwards', () => {
    expect(assignEventLanes([ev(13.5, 14), ev(12, 13), ev(11, 12.5), ev(11.5, 13)])).toEqual([
      { currentLane: 0, totalLanes: 1 },
      { currentLane: 2, totalLanes: 3 },
      { currentLane: 0, totalLanes: 3 },
      { currentLane: 1, totalLanes: 3 },
    ]);
  });

  it('treats short events as lasting the minimum duration', () => {
    // 09:00-09:05, 09:02-09:30 and 09:06-09:10 with a 20 minute minimum
    const events = [ev(9, 9 + 5 / 60), ev(9 + 2 / 60, 9.5), ev(9 + 6 / 60, 9 + 10 / 60)];
    expect(assignEventLanes(events)).toEqual([
      { currentLane: 0, totalLanes: 2 },
      { currentLane: 1, totalLanes: 2 },
      { currentLane: 0, totalLanes: 2 },
    ]);
    expect(assignEventLanes(events, 20 * 60000)).toEqual([
      { currentLane: 0, totalLanes: 3 },
      { currentLane: 1, totalLanes: 3 },
      { currentLane: 2, totalLanes: 3 },
    ]);
  });
});
