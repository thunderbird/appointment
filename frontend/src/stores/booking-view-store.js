import { defineStore } from 'pinia';
import { ref, inject } from 'vue';
import { bookingCalendarViews } from '@/definitions';

/**
 * Store for BookingView and its tightly coupled components.
 */
// eslint-disable-next-line import/prefer-default-export
export const useBookingViewStore = defineStore('bookingView', () => {
  const dj = inject('dayjs');

  // States
  const activeView = ref(bookingCalendarViews.loading);
  const activeDate = ref(dj());
  // Data
  const selectedEvent = ref(null);
  const appointment = ref(null);
  const attendee = ref(null);

  const $reset = () => {
    activeView.value = bookingCalendarViews.loading;
    activeDate.value = dj();
    selectedEvent.value = null;
    appointment.value = null;
    attendee.value = null;
  };

  return {
    // State
    activeView,
    activeDate,
    // Data
    selectedEvent,
    appointment,
    attendee,
    // Funcs
    $reset,
  };
});
