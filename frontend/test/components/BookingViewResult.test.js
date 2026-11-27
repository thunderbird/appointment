import { afterEach, describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia } from 'pinia';
import dayjs from 'dayjs';
import timezone from 'dayjs/plugin/timezone';
import utc from 'dayjs/plugin/utc';
import i18ninstance from '@/composables/i18n';
import router from '@/router';
import { apiUrlKey, dayjsKey } from '@/keys';
import { BookingResultState } from '@/definitions';
import BookingViewResult from '@/views/BookerView/components/BookingViewResult.vue';

dayjs.extend(utc);
dayjs.extend(timezone);

describe('BookingViewResult', () => {
  let wrapper;

  afterEach(() => {
    wrapper?.unmount();
  });

  const mountResult = (state) =>
    mount(BookingViewResult, {
      props: {
        selectedEvent: { start: '2026-12-01T10:00:00Z', duration: 30, id: 42, slug: 'abc' },
        attendee: { name: 'Jane', email: 'jane@example.org' },
        state,
      },
      global: {
        plugins: [createPinia(), i18ninstance, router],
        provide: {
          [apiUrlKey]: 'http://localhost:5000',
          [dayjsKey]: dayjs,
        },
      },
    });

  it.each([
    [BookingResultState.Requested, 'Booking request sent', 'Your host has been notified.'],
    [BookingResultState.Confirmed, 'Booking confirmed', 'jane@example.org'],
  ])('shows heading, description and calendar download for %s bookings', (state, heading, description) => {
    wrapper = mountResult(state);

    expect(wrapper.get('[data-testid="booking-view-result-heading"]').text()).toBe(heading);
    expect(wrapper.get('[data-testid="booking-view-result-heading"] svg').exists()).toBe(true);
    expect(wrapper.text()).toContain(description);
    expect(wrapper.find('.actions').exists()).toBe(true);
  });

  it('shows a cancelled booking without icon and actions', () => {
    wrapper = mountResult(BookingResultState.Cancelled);

    expect(wrapper.get('[data-testid="booking-view-result-heading"]').text()).toBe('Booking cancelled');
    expect(wrapper.find('[data-testid="booking-view-result-heading"] svg').exists()).toBe(false);
    expect(wrapper.text()).toContain('This appointment has been cancelled.');
    expect(wrapper.text()).toContain('Virtual meeting with Jane');
    expect(wrapper.find('.actions').exists()).toBe(false);
  });
});
