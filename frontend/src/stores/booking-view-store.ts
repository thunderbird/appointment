import { Dayjs, ConfigType } from 'dayjs';
import { defineStore } from 'pinia';
import { ref, inject } from 'vue';
import { bookingCalendarViews } from '@/definitions';
import { Appointment, Attendee } from '@/models';
import { dayjsKey } from '@/keys';

/**
 * Store for BookingView and its tightly coupled components.
 */
// eslint-disable-next-line import/prefer-default-export
export const useBookingViewStore = defineStore('bookingView', () => {
  const dj = inject(dayjsKey);

  // States
  const activeView = ref(bookingCalendarViews.loading);
  const activeDate = ref(dj());
  // Data
  const selectedEvent = ref<Dayjs>(null);
  const appointment = ref<Appointment>(null);
  const attendee = ref<Attendee>(null);

  /**
   * Restore default state, set date to today and remove other data
   */
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
