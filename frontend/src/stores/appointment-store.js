import { defineStore } from 'pinia';
import { ref, computed, inject } from 'vue';
import { appointmentState } from '@/definitions';
import { useUserStore } from '@/stores/user-store';

// eslint-disable-next-line import/prefer-default-export
export const useAppointmentStore = defineStore('appointments', () => {
  const dj = inject('dayjs');

  // State
  const isLoaded = ref(false);

  // Data
  const appointments = ref([]);
  const pendingAppointments = computed(
    () => appointments.value.filter((a) => a.status === appointmentState.pending),
  );

  /**
   * Retrieve appointment status from related time slots
   * @param {object} appointment Single appointment object
   * @returns {appointmentState}
   */
  const status = (appointment) => {
    // check past events
    if (appointment.slots.filter((s) => dj(s.start).isAfter(dj())).length === 0) {
      return appointmentState.past;
    }
    // check booked events
    if (appointment.slots.filter((s) => s.attendee_id != null).length > 0) {
      return appointmentState.booked;
    }
    // else event is still wating to be booked
    return appointmentState.pending;
  };

  /**
   * Append additional data to retrieved appointments
   */
  const postFetchProcess = async () => {
    const userStore = useUserStore();

    appointments.value.forEach((a) => {
      a.status = status(a);
      a.active = a.status !== appointmentState.past; // TODO
      // convert start dates from UTC back to users timezone
      a.slots.forEach((s) => {
        s.start = dj.utc(s.start).tz(userStore.data.timezone ?? dj.tz.guess());
      });
    });
  };

  /**
   * Get all appointments for current user
   * @param {function} call preconfigured API fetch function
   */
  const fetch = async (call) => {
    const { data, error } = await call('me/appointments').get().json();
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

  return {
    isLoaded, appointments, pendingAppointments, status, postFetchProcess, fetch, $reset,
  };
});
