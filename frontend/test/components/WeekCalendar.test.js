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

  it('displays "Busy" for remote events and all-day remote events, but retains title for pending appointments', () => {
    wrapper = mount(
      WeekCalendar,
      getMountOptions({
        events: [
          { title: 'Personal Dentist', start: '2026-11-10T09:00:00+00:00', end: '2026-11-10T10:00:00+00:00' },
          { title: 'Holiday', start: '2026-11-10', end: '2026-11-10', all_day: true },
        ],
        pendingAppointments: [
          {
            id: 1,
            title: 'Consultation Call',
            duration: 30,
            slots: [{ start: dayjs('2026-11-10T14:00:00Z').tz('Europe/London'), duration: 30 }],
          },
        ],
      })
    );

    expect(wrapper.get('.remote-event').text()).toBe('Busy');
    expect(wrapper.get('.all-day-event-item').text()).toBe('Busy');
    expect(wrapper.get('.pending-appointment').text()).toBe('Consultation Call');
  });

  it('limits popup information and applies remote-event-popup class when hovering remote events', async () => {
    wrapper = mount(
      WeekCalendar,
      getMountOptions({
        events: [
          {
            title: 'Private Lunch',
            calendar_title: 'Personal Cal',
            start: '2026-11-10T09:00:00+00:00',
            end: '2026-11-10T10:00:00+00:00',
          },
        ],
      })
    );

    await wrapper.get('.remote-event').trigger('mouseenter');
    const popup = wrapper.find('.event-popup');
    expect(popup.exists()).toBe(true);
    expect(popup.classes()).toContain('remote-event-popup');
    expect(popup.find('.event-title').text()).toBe('Busy');
  });
});
