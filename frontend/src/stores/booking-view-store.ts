import { defineStore } from 'pinia';
import { ref, inject } from 'vue';
import { BookingCalendarView } from '@/definitions';
import { Appointment, AppointmentResponse, Attendee, Fetch, Slot, SlotResponse } from '@/models';
import { dayjsKey } from '@/keys';

/**
 * Store for BookingView and its tightly coupled components.
 */
 
export const useBookingViewStore = defineStore('bookingView', () => {
  const dj = inject(dayjsKey);

  // States
  const activeView = ref(BookingCalendarView.Loading);
  const activeDate = ref(dj());
  const call = ref(null);

  // Data
  const selectedEvent = ref<Appointment & Slot>(null); // The selected slot also needs some data from its parent
  const appointment = ref<Appointment>(null);
  const attendee = ref<Attendee>(null);

  /**
   * Initialize store with data required at runtime
   *
   * @param fetch preconfigured function to perform API calls
   */
  const init = (fetch: Fetch) => {
    call.value = fetch;
  }

  /**
   * Gets appointment object to check available slots
   */
  const getAppointmentAvailability = async (url: string) => {
    const request: AppointmentResponse = call.value('schedule/public/availability', {
      headers: {
        'Cache-control': 'no-store'
      }
    }).post({ url });

    return await request.json();
  }

  /**
   * Request available slot for booking
   */
  const putAvailabilityRequest = async (obj, url) => {
    const request: SlotResponse = call.value('schedule/public/availability/request', {
      headers: {
        'Cache-control': 'no-store'
      }
    }).put({
      s_a: obj,
      url,
    });

    return await request.json();
  }

  /**
   * Restore default state, set date to today and remove other data
   */
  const $reset = () => {
    activeView.value = BookingCalendarView.Loading;
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
    init,
    getAppointmentAvailability,
    putAvailabilityRequest,
    $reset,
  };
});

export const createBookingViewStore = (call: Fetch) => {
  const store = useBookingViewStore();
  store.init(call);
  return store;
};
