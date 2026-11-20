import { afterEach, describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia } from 'pinia';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import i18ninstance from '@/composables/i18n';
import useDayJS from '@/composables/dayjs';
import WeekCalendar from '@/views/DashboardView/components/WeekCalendar.vue';

// Needed to create pending appointment slots before mounting, like the appointment store does
dayjs.extend(utc);
dayjs.extend(timezone);

describe('WeekCalendar', () => {
  let wrapper;

  // Tests run in America/Vancouver (see vitest.global-setup.ts), so the display timezone differs from the system one
  const getMountOptions = (props = {}) => ({
    props: {
      activeDateRange: { start: '2026-11-08', end: '2026-11-14' },
      timezone: 'Europe/London',
      ...props,
    },
    global: {
      plugins: [createPinia(), i18ninstance, { install: (app) => useDayJS(app, 'en') }],
    },
  });

  // Returns grid column and row of an event element
  const gridPosition = (el) => ({
    column: el.element.style.gridColumn,
    row: el.element.style.gridRowStart,
  });

  afterEach(() => {
    wrapper?.unmount();
  });

  it('draws remote events and pending appointments at the same time in the given timezone', () => {
    wrapper = mount(
      WeekCalendar,
      getMountOptions({
        events: [{ title: 'Remote', start: '2026-11-10T09:00:00+00:00', end: '2026-11-10T09:30:00+00:00' }],
        pendingAppointments: [
          {
            id: 1,
            title: 'Pending',
            duration: 30,
            slots: [{ start: dayjs('2026-11-10T09:00:00Z').tz('Europe/London'), duration: 30 }],
          },
        ],
      })
    );

    const remote = wrapper.get('.remote-event');
    const pending = wrapper.get('.pending-appointment');

    // Tuesday is the third day column (column 1 holds the time labels), 09:00 is row 10
    expect(gridPosition(remote)).toEqual({ column: '4', row: '10' });
    expect(gridPosition(pending)).toEqual(gridPosition(remote));
  });

  it('places events in the day column of the given timezone', () => {
    wrapper = mount(
      WeekCalendar,
      getMountOptions({
        // Friday 02:00 in London, but still Thursday in Vancouver
        events: [{ title: 'Remote', start: '2026-11-13T02:00:00+00:00', end: '2026-11-13T03:00:00+00:00' }],
      })
    );

    expect(gridPosition(wrapper.get('.remote-event'))).toEqual({ column: '7', row: '3' });
  });

  it('splits multi-day events across calendar day columns and clamps height to day boundaries', () => {
    wrapper = mount(
      WeekCalendar,
      getMountOptions({
        events: [
          {
            title: 'Multi-Day Workshop',
            start: '2026-11-10T09:00:00+00:00', // Tuesday 09:00
            end: '2026-11-12T15:00:00+00:00', // Thursday 15:00
          },
        ],
      })
    );

    const remoteEvents = wrapper.findAll('.remote-event');
    expect(remoteEvents).toHaveLength(3);

    // Tuesday: Column 4 (Tue), starts at 09:00 (row 10), duration 15h = 900px (- 2px gap = 898px)
    expect(gridPosition(remoteEvents[0])).toEqual({ column: '4', row: '10' });
    expect(remoteEvents[0].element.style.height).toBe('max(1.5rem, 898px)');

    // Wednesday: Column 5 (Wed), starts at 00:00 (row 1), duration 24h = 1440px (- 2px gap = 1438px)
    expect(gridPosition(remoteEvents[1])).toEqual({ column: '5', row: '1' });
    expect(remoteEvents[1].element.style.height).toBe('max(1.5rem, 1438px)');

    // Thursday: Column 6 (Thu), starts at 00:00 (row 1), duration 15h = 900px (- 2px gap = 898px)
    expect(gridPosition(remoteEvents[2])).toEqual({ column: '6', row: '1' });
    expect(remoteEvents[2].element.style.height).toBe('max(1.5rem, 898px)');
  });

  it('isolates lane calculations across midnight boundary', () => {
    wrapper = mount(
      WeekCalendar,
      getMountOptions({
        events: [
          {
            title: 'Late Night Event',
            start: '2026-11-10T23:45:00+00:00', // Tuesday 23:45 - 23:55
            end: '2026-11-10T23:55:00+00:00',
          },
          {
            title: 'Early Morning Event',
            start: '2026-11-11T00:05:00+00:00', // Wednesday 00:05 - 00:15 (only 10 mins apart across midnight)
            end: '2026-11-11T00:15:00+00:00',
          },
        ],
      })
    );

    const remoteEvents = wrapper.findAll('.remote-event');
    expect(remoteEvents).toHaveLength(2);

    const tuesdayEvent = remoteEvents.find((el) => gridPosition(el).column === '4');
    const wednesdayEvent = remoteEvents.find((el) => gridPosition(el).column === '5');

    // Both events must retain full width (1 total lane) because the midnight boundary isolates lanes per day
    expect(tuesdayEvent.element.style.getPropertyValue('--total-lanes')).toBe('1');
    expect(tuesdayEvent.element.style.getPropertyValue('--current-lane')).toBe('0');
    expect(wednesdayEvent.element.style.getPropertyValue('--total-lanes')).toBe('1');
    expect(wednesdayEvent.element.style.getPropertyValue('--current-lane')).toBe('0');
  });

  it('spans all 24 visual grid rows on Daylight Saving Time transition days', () => {
    // March 29, 2026 is the spring-forward DST transition day in Europe/London (only 23 elapsed hours)
    wrapper = mount(
      WeekCalendar,
      getMountOptions({
        activeDateRange: { start: '2026-03-29', end: '2026-04-04' },
        timezone: 'Europe/London',
        events: [
          {
            title: 'Full Day Event on DST day',
            start: '2026-03-29T00:00:00+00:00',
            end: '2026-03-30T00:00:00+01:00',
          },
        ],
      })
    );

    const remoteEvents = wrapper.findAll('.remote-event');
    expect(remoteEvents).toHaveLength(1);
    // Even though elapsed time is 23h, visual grid height must cover all 24 visual rows (1440px - 2px gap = 1438px)
    expect(remoteEvents[0].element.style.height).toBe('max(1.5rem, 1438px)');
  });

  it('preserves positive duration for bookings crossing the repeated fall-back DST hour', () => {
    // October 25, 2026 is the autumn fall-back DST transition day in Europe/London.
    // At 02:00 BST (+01:00), clocks move back 1 hour to 01:00 GMT (+00:00).
    // A booking from 01:30+01:00 to 01:15+00:00 lasts 45 physical minutes.
    wrapper = mount(
      WeekCalendar,
      getMountOptions({
        activeDateRange: { start: '2026-10-25', end: '2026-10-31' },
        timezone: 'Europe/London',
        events: [
          {
            title: 'Repeated Hour Booking',
            start: '2026-10-25T01:30:00+01:00',
            end: '2026-10-25T01:15:00+00:00',
          },
        ],
      })
    );

    const remoteEvents = wrapper.findAll('.remote-event');
    expect(remoteEvents).toHaveLength(1);
    // 45 minutes duration = 45px - 2px gap = 43px height (instead of collapsing to minimum height)
    expect(remoteEvents[0].element.style.height).toBe('max(1.5rem, 43px)');
  });

  it('keeps all-day events on the correct calendar date regardless of display timezone', () => {
    wrapper = mount(
      WeekCalendar,
      getMountOptions({
        activeDateRange: { start: '2026-11-08', end: '2026-11-14' },
        timezone: 'America/Vancouver', // Vancouver is 8 hours behind London/UTC
        events: [
          {
            title: 'All-Day Holiday',
            start: '2026-11-10',
            end: '2026-11-11',
            all_day: true,
          },
        ],
      })
    );

    const allDayItems = wrapper.findAll('.all-day-event-item');
    expect(allDayItems).toHaveLength(1);

    // Tuesday Nov 10 is the 3rd day column (index 2 in weekdays, Sun=0, Mon=1, Tue=2)
    // The parent weekday header for Tuesday is at gridColumn: 4
    const parentHeader = allDayItems[0].element.closest('.calendar-weekday-header');
    expect(parentHeader.style.gridColumn).toBe('4');
  });
});
