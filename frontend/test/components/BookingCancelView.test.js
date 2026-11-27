import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import { createPinia } from 'pinia';
import { createMemoryHistory, createRouter } from 'vue-router';
import { ref } from 'vue';
import dayjs from 'dayjs';
import timezone from 'dayjs/plugin/timezone';
import utc from 'dayjs/plugin/utc';
import i18ninstance from '@/composables/i18n';
import { apiUrlKey, callKey, dayjsKey } from '@/keys';
import { BookingStatus } from '@/definitions';
import BookingCancelView from '@/views/BookingCancelView.vue';

dayjs.extend(utc);
dayjs.extend(timezone);

describe('BookingCancelView', () => {
  let wrapper;
  let router;

  // Minimal router without the app's global navigation guards
  beforeEach(async () => {
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'home', component: { template: '<div />' } },
        { path: '/booking/cancel/:slot/:token', name: 'booking-cancel', component: BookingCancelView },
      ],
    });
    await router.push('/booking/cancel/42/tkn');
    await router.isReady();
  });

  afterEach(() => {
    wrapper?.unmount();
  });

  // Mocks the call injection, returning the given response for the details request
  const mountView = (response) => {
    const json = vi.fn().mockResolvedValue(response);
    const post = vi.fn().mockReturnValue({ json });
    const call = vi.fn().mockReturnValue({ post });

    wrapper = mount(BookingCancelView, {
      global: {
        plugins: [createPinia(), i18ninstance, router],
        provide: {
          [apiUrlKey]: 'http://localhost:5000',
          [callKey]: call,
          [dayjsKey]: dayjs,
        },
      },
    });

    return { call, post };
  };

  const details = (bookingStatus) => ({
    data: ref({
      slot: { id: 42, slug: 'abc', booking_status: bookingStatus, start: '2026-12-01T10:00:00', duration: 30 },
      attendee: { name: 'Jane', email: 'jane@example.org' },
    }),
    error: ref(null),
  });

  it.each([
    [BookingStatus.Requested, 'This booking request is currently pending a response from the host.'],
    [BookingStatus.Booked, 'This booking request has been confirmed.'],
  ])('loads the booking details with the token from the url (status %s)', async (bookingStatus, description) => {
    const { call, post } = mountView(details(bookingStatus));
    await flushPromises();

    expect(call).toHaveBeenCalledWith('schedule/public/availability/cancel/details');
    expect(post).toHaveBeenCalledWith({ slot_id: 42, slot_token: 'tkn' });

    // Neutral texts instead of the success texts shown right after booking
    expect(wrapper.get('[data-testid="booking-view-result-heading"]').text()).toBe('Booking request');
    expect(wrapper.find('[data-testid="booking-view-result-heading"] svg').exists()).toBe(false);
    expect(wrapper.text()).toContain(description);
    expect(wrapper.text()).toContain('Virtual meeting with Jane');

    // The cancel modal is shown right away
    expect(wrapper.find('[data-testid="booking-cancel-confirm-btn"]').exists()).toBe(true);
  });

  it('shows an error for an invalid or closed booking', async () => {
    mountView({ data: ref({ detail: { message: 'Slot not found' } }), error: ref(true) });
    await flushPromises();

    expect(wrapper.get('h1').text()).toBe('This cancellation link is invalid.');
    expect(wrapper.find('[data-testid="booking-view-result-heading"]').exists()).toBe(false);
    expect(wrapper.find('[data-testid="booking-cancel-confirm-btn"]').exists()).toBe(false);
  });
});
