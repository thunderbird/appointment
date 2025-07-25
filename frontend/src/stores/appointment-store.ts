import { defineStore } from 'pinia';
import { ref, computed, inject } from 'vue';
import { BookingStatus, MetricEvents } from '@/definitions';
import { useUserStore } from '@/stores/user-store';
import {
  Appointment, AppointmentListResponse, Fetch, Slot,
  AvailabilitySlotResponse,
} from '@/models';
import { dayjsKey, tzGuessKey } from '@/keys';
import { usePosthog, posthog } from '@/composables/posthog';

 
export const useAppointmentStore = defineStore('appointments', () => {
  const dj = inject(dayjsKey);
  const tzGuess = inject(tzGuessKey);
  const call = ref(null);

  // State
  const isLoaded = ref(false);

  // Data
  const appointments = ref<Appointment[]>([]);
  const pendingAppointments = computed(
    (): Appointment[] => appointments.value.filter((a) => a?.slots[0]?.booking_status === BookingStatus.Requested),
  );
  const pendingFutureAppointments = computed(
    (): Appointment[] => pendingAppointments.value.filter((a) => a?.slots[0]?.start > dj()),
  );
  const selectedAppointment = ref<Appointment | null>(null);

  /**
   * Initialize store with data required at runtime
   *
   * @param fetch preconfigured function to perform API calls
   */
    const init = (fetch: Fetch) => {
      call.value = fetch;
    }

  /**
   * Append additional data to retrieved appointments
   */
  const postFetchProcess = async () => {
    const userStore = useUserStore();

    appointments.value.forEach((a) => {
      a.active = a.status !== BookingStatus.Booked;
      // convert start dates from UTC back to users timezone
      a.slots.forEach((s: Slot) => {
        s.start = dj(s.start).utc(true).tz(userStore.data.settings.timezone ?? tzGuess);
      });
    });

    // Update selectedAppointment with the latest data
    if (selectedAppointment.value) {
      const appointment = appointments.value.find((a) => a.id === selectedAppointment.value.id);
      selectedAppointment.value = appointment ?? null;
    }
  };

  /**
   * Get all appointments for current user
   */
  const fetch = async () => {
    const { data, error }: AppointmentListResponse = await call.value('me/appointments').get().json();
    if (!error.value) {
      if (data.value === null || typeof data.value === 'undefined') return;
      appointments.value = data.value;
      isLoaded.value = true;
    }
    // After we fetch the data, apply some processing
    await postFetchProcess();
  };

  /**
   * Restore default state, empty and unload appointments
   */
  const $reset = () => {
    appointments.value = [];
    isLoaded.value = false;
  };

  /**
   * Remove an appointment and all assigned time slots
   */
  const deleteAppointment = async (id: number) => {
    await call.value(`apmt/${id}`).delete();
    await fetch();
  };

  /**
   * Confirm or deny a booking slot
   */
  const confirmOrDenyBooking = async ({ slotId, slotToken, ownerUrl, confirmed }) => {
    const obj = {
      slot_id: slotId,
      slot_token: slotToken,
      owner_url: ownerUrl,
      confirmed,
    };
    const { error, data }: AvailabilitySlotResponse = await call.value('schedule/public/availability/booking').put(obj).json();

    if (usePosthog && !error.value) {
      const event = confirmed ? MetricEvents.ConfirmBooking : MetricEvents.DenyBooking;
      posthog.capture(event);
    }

    await fetch();

    return { error, data };
  };

  /**
   * Cancel an appointment (booking context)
   */
  const cancelAppointment = async (appointmentId: number) => {
    const { error } = await call.value(`apmt/${appointmentId}/cancel`).post().json();

    if (usePosthog && !error.value) {
      posthog.capture(MetricEvents.CancelBooking);
    }

    await fetch();

    return { error };
  };

  /**
   * Modify an appointment (booking context)
   */
  const modifyBookingAppointment = async ({ appointmentId, title, start, slotId, notes }) => {
    const payload = { title, start, slot_id: slotId, notes };

    const { error } = await call.value(`apmt/${appointmentId}/modify`).put(payload).json();

    if (usePosthog && !error.value) {
      posthog.capture(MetricEvents.ModifyBooking);
    }

    await fetch();

    return { error };
  };

  /**
   * Fetch available slots for a given day
   */
  const fetchAvailabilityForDay = async (date: string) => {
    const { data, error } = await call.value(`/schedule/availability_for_day?date=${date}`).get().json();
    return { data, error };
  };

  return {
    isLoaded,
    appointments,
    selectedAppointment,
    pendingAppointments,
    pendingFutureAppointments,
    init,
    postFetchProcess,
    fetch,
    $reset,
    deleteAppointment,
    cancelAppointment,
    confirmOrDenyBooking,
    modifyBookingAppointment,
    fetchAvailabilityForDay,
  };
});

export const createAppointmentStore = (call: Fetch) => {
  const store = useAppointmentStore();
  store.init(call);
  return store;
};
