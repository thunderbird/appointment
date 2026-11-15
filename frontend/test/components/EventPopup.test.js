import { afterEach, describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import i18ninstance from '@/composables/i18n';
import useDayJS from '@/composables/dayjs';
import EventPopup from '@/elements/EventPopup.vue';

describe('EventPopup', () => {
  let wrapper;

  const mountPopup = (customData = {}) =>
    mount(EventPopup, {
      props: {
        event: {
          id: 1,
          title: 'Team Meeting',
          colourScheme: 'blue',
          description: '',
          with: '',
          time: {
            start: '2026-11-10T09:00:00+00:00',
            end: '2026-11-10T10:00:00+00:00',
          },
          customData: {
            calendar_title: 'Work Calendar',
            calendar_color: '#3b82f6',
            duration: 60,
            preview: false,
            all_day: false,
            slot_status: 1,
            booking_status: 1,
            tentative: false,
            remote: false,
            ...customData,
          },
        },
      },
      global: {
        plugins: [i18ninstance, { install: (app) => useDayJS(app, 'en') }],
      },
    });

  afterEach(() => {
    wrapper?.unmount();
  });

  it('shows guest details when attendee is present for non-remote events', () => {
    wrapper = mountPopup({
      remote: false,
      attendee: { name: 'John Doe', email: 'john@example.com' },
    });

    expect(wrapper.classes()).not.toContain('remote-event-popup');
    expect(wrapper.text()).toContain('1 guest');
  });

  it('hides guest details and applies remote styling when event is remote', () => {
    wrapper = mountPopup({
      remote: true,
      attendee: { name: 'John Doe', email: 'john@example.com' },
    });

    expect(wrapper.classes()).toContain('remote-event-popup');
    expect(wrapper.text()).not.toContain('1 guest');
  });
});
