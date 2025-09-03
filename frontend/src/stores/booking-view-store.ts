import { defineStore } from 'pinia';
import { ref, inject } from 'vue';
import { BookingCalendarView } from '@/definitions';
import { Appointment, Attendee, Slot } from '@/models';
import { dayjsKey } from '@/keys';

/**
 * Store for BookingView and its tightly coupled components.
 */
 
export const useBookingViewStore = defineStore('bookingView', () => {
  const dj = inject(dayjsKey);

  // States
  const activeView = ref(BookingCalendarView.Loading);
  const activeDate = ref(dj());

  // Data
  const selectedEvent = ref<Appointment & Slot>(null); // The selected slot also needs some data from its parent
  const appointment = ref<Appointment>(null);
  const attendee = ref<Attendee>(null); // Attendee can either be a guest or an actual user
  const guestUserInfo = ref<{ name?: string, email: string }>({ name: '', email: '' }); // Used in the SlotSelectionUserInfo form
  const guestUserInfoValid = ref<boolean>(false); // Used in the SlotSelectionUserInfo form

  /**
   * Restore default state, set date to today and remove other data
   */
  const $reset = () => {
    activeView.value = BookingCalendarView.Loading;
    activeDate.value = dj();
    selectedEvent.value = null;
    appointment.value = null;
    attendee.value = null;
    guestUserInfo.value = { name: '', email: '' };
  };

  return {
    // State
    activeView,
    activeDate,
    // Data
    selectedEvent,
    appointment,
    attendee,
    guestUserInfo,
    guestUserInfoValid,
    // Funcs
    $reset,
  };
});
