import { describe, it, test, expect, afterEach } from 'vitest';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import { assignEventLanes, splitEventIntoDaySegments, timeFormat } from '@/utils';

dayjs.extend(utc);
dayjs.extend(timezone);

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

  it('places longer events first when they start at the same time', () => {
    expect(assignEventLanes([ev(12, 12.5), ev(12, 14), ev(12, 13)])).toEqual([
      { currentLane: 2, totalLanes: 3 },
      { currentLane: 0, totalLanes: 3 },
      { currentLane: 1, totalLanes: 3 },
    ]);
  });
});

describe('splitEventIntoDaySegments', () => {
  const tz = 'UTC';
  const weekdays = [
    dayjs.tz('2026-11-15', tz), // Sun
    dayjs.tz('2026-11-16', tz), // Mon
    dayjs.tz('2026-11-17', tz), // Tue
    dayjs.tz('2026-11-18', tz), // Wed
    dayjs.tz('2026-11-19', tz), // Thu
    dayjs.tz('2026-11-20', tz), // Fri
    dayjs.tz('2026-11-21', tz), // Sat
  ];

  it('keeps single-day event as a single segment', () => {
    const event = {
      title: 'Meeting',
      start: '2026-11-17T10:00:00Z',
      end: '2026-11-17T11:30:00Z',
    };

    const segments = splitEventIntoDaySegments(event, weekdays, dayjs, tz);
    expect(segments).toHaveLength(1);
    expect(segments[0].title).toBe('Meeting');
    expect(segments[0].start).toBe(dayjs.tz('2026-11-17T10:00:00Z', tz).format());
    expect(segments[0].end).toBe(dayjs.tz('2026-11-17T11:30:00Z', tz).format());
    expect(segments[0].originalStart).toBe(event.start);
    expect(segments[0].originalEnd).toBe(event.end);
  });

  test.each([
    {
      description: 'splits multi-day event into daily segments bounded by day boundaries',
      event: { title: 'Conference', start: '2026-11-17T09:00:00Z', end: '2026-11-19T15:00:00Z' },
      expected: [
        ['2026-11-17T09:00:00Z', '2026-11-18T00:00:00Z'],
        ['2026-11-18T00:00:00Z', '2026-11-19T00:00:00Z'],
        ['2026-11-19T00:00:00Z', '2026-11-19T15:00:00Z'],
      ],
    },
    {
      description: 'splits overnight event crossing midnight into two segments',
      event: { title: 'Night Shift', start: '2026-11-17T22:00:00Z', end: '2026-11-18T04:00:00Z' },
      expected: [
        ['2026-11-17T22:00:00Z', '2026-11-18T00:00:00Z'],
        ['2026-11-18T00:00:00Z', '2026-11-18T04:00:00Z'],
      ],
    },
    {
      description: 'does not create an empty segment if an event ends exactly at midnight',
      event: { title: 'Late Evening', start: '2026-11-17T20:00:00Z', end: '2026-11-18T00:00:00Z' },
      expected: [['2026-11-17T20:00:00Z', '2026-11-18T00:00:00Z']],
    },
    {
      description: 'includes segments within the active week for events starting before the week',
      event: { title: 'Ongoing Event', start: '2026-11-14T10:00:00Z', end: '2026-11-16T12:00:00Z' },
      expected: [
        ['2026-11-15T00:00:00Z', '2026-11-16T00:00:00Z'],
        ['2026-11-16T00:00:00Z', '2026-11-16T12:00:00Z'],
      ],
    },
    {
      description: 'retains zero-length events with equal endpoints as a single visible segment',
      event: { title: 'Reminder', start: '2026-11-17T10:00:00Z', end: '2026-11-17T10:00:00Z' },
      expected: [['2026-11-17T10:00:00Z', '2026-11-17T10:00:00Z']],
    },
  ])('$description', ({ event, expected }) => {
    const segments = splitEventIntoDaySegments(event, weekdays, dayjs, tz);
    expect(segments.map((s) => [s.start, s.end])).toEqual(
      expected.map(([start, end]) => [dayjs.tz(start, tz).format(), dayjs.tz(end, tz).format()])
    );
    expect(segments.every((s) => s.originalStart === event.start && s.originalEnd === event.end)).toBe(true);
  });

  it('returns empty array for invalid or non-chronological events', () => {
    expect(splitEventIntoDaySegments({ start: 'invalid', end: 'invalid' }, weekdays, dayjs)).toEqual([]);
    expect(
      splitEventIntoDaySegments(
        { start: '2026-11-17T12:00:00Z', end: '2026-11-17T10:00:00Z' },
        weekdays,
        dayjs
      )
    ).toEqual([]);
  });
});
