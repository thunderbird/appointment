import { afterEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import { ref } from 'vue';
import { createPinia } from 'pinia';
import dayjs from 'dayjs';
import timezone from 'dayjs/plugin/timezone';
import utc from 'dayjs/plugin/utc';
import i18ninstance from '@/composables/i18n';
import router from '@/router';
import { apiUrlKey, callKey, dayjsKey } from '@/keys';
import { BookingResultState } from '@/definitions';
import BookingViewResult from '@/views/BookerView/components/BookingViewResult.vue';

dayjs.extend(utc);
dayjs.extend(timezone);

describe('BookingViewResult', () => {
  let wrapper;

  afterEach(() => {
    wrapper?.unmount();
  });

  const mountResult = (state, selectedEvent = {}, call = vi.fn(), props = {}) =>
    mount(BookingViewResult, {
      props: {
        selectedEvent: { start: '2026-12-01T10:00:00Z', duration: 30, id: 42, slug: 'abc', ...selectedEvent },
        attendee: { name: 'Jane', email: 'jane@example.org' },
        state,
        ...props,
      },
      global: {
        plugins: [createPinia(), i18ninstance, router],
        provide: {
          [apiUrlKey]: 'http://localhost:5000',
          [callKey]: call,
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

  // Mocks the call injection, returning the given response for the cancel request
  const mockCall = (response) => {
    const json = vi.fn().mockResolvedValue(response);
    const put = vi.fn().mockReturnValue({ json });
    return { call: vi.fn().mockReturnValue({ put }), put };
  };

  it.each([BookingResultState.Requested, BookingResultState.Confirmed])(
    'shows the cancel link for %s bookings with a token',
    (state) => {
      wrapper = mountResult(state, { booking_tkn: 'tkn' });

      expect(wrapper.get('[data-testid="booking-view-cancel-link"]').text()).toBe('Need to cancel?');
    }
  );

  it('hides the cancel link without a booking token', () => {
    wrapper = mountResult(BookingResultState.Confirmed);

    expect(wrapper.find('[data-testid="booking-view-cancel-link"]').exists()).toBe(false);
  });

  it('cancels the booking after confirming in the modal', async () => {
    const { call, put } = mockCall({ data: ref({}), error: ref(null) });
    wrapper = mountResult(BookingResultState.Confirmed, { booking_tkn: 'tkn' }, call);

    await wrapper.get('[data-testid="booking-view-cancel-link"]').trigger('click');
    await wrapper.get('[data-testid="booking-cancel-confirm-btn"]').trigger('click');
    await flushPromises();

    expect(call).toHaveBeenCalledWith('schedule/public/availability/cancel');
    expect(put).toHaveBeenCalledWith({ slot_id: 42, slot_token: 'tkn' });
    expect(wrapper.get('[data-testid="booking-view-result-heading"]').text()).toBe('Booking cancelled');
    expect(wrapper.find('[data-testid="booking-view-cancel-link"]').exists()).toBe(false);
  });

  it('shows the backend error in the modal if cancelling fails', async () => {
    const { call } = mockCall({ data: ref({ detail: { message: 'Slot not found' } }), error: ref(true) });
    wrapper = mountResult(BookingResultState.Confirmed, { booking_tkn: 'tkn' }, call);

    await wrapper.get('[data-testid="booking-view-cancel-link"]').trigger('click');
    await wrapper.get('[data-testid="booking-cancel-confirm-btn"]').trigger('click');
    await flushPromises();

    expect(wrapper.get('.booking-cancel-modal').text()).toContain('Slot not found');
    expect(wrapper.get('[data-testid="booking-view-result-heading"]').text()).toBe('Booking confirmed');
  });

  it('shows custom texts without icon until the booking is cancelled', async () => {
    const { call } = mockCall({ data: ref({}), error: ref(null) });
    wrapper = mountResult(BookingResultState.Requested, { booking_tkn: 'tkn' }, call, {
      customHeading: 'Custom heading',
      customDescription: 'Custom description',
    });

    expect(wrapper.get('[data-testid="booking-view-result-heading"]').text()).toBe('Custom heading');
    expect(wrapper.find('[data-testid="booking-view-result-heading"] svg').exists()).toBe(false);
    expect(wrapper.text()).toContain('Custom description');

    await wrapper.get('[data-testid="booking-view-cancel-link"]').trigger('click');
    await wrapper.get('[data-testid="booking-cancel-confirm-btn"]').trigger('click');
    await flushPromises();

    // After cancelling, the cancelled texts replace the custom ones
    expect(wrapper.get('[data-testid="booking-view-result-heading"]').text()).toBe('Booking cancelled');
    expect(wrapper.text()).toContain('This appointment has been cancelled.');
    expect(wrapper.text()).not.toContain('Custom description');
  });

  it.each([
    [{ booking_tkn: 'tkn' }, true],
    [{}, false],
  ])('opens the cancel modal on mount if requested and possible (%o)', async (selectedEvent, opened) => {
    wrapper = mountResult(BookingResultState.Confirmed, selectedEvent, vi.fn(), { openCancelModal: true });
    await flushPromises();

    expect(wrapper.find('[data-testid="booking-cancel-confirm-btn"]').exists()).toBe(opened);
  });

  it('does not open the cancel modal on mount by default', async () => {
    wrapper = mountResult(BookingResultState.Confirmed, { booking_tkn: 'tkn' });
    await flushPromises();

    expect(wrapper.find('[data-testid="booking-cancel-confirm-btn"]').exists()).toBe(false);
  });
});
