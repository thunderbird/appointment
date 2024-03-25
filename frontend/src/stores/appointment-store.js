import { defineStore } from 'pinia';
import { ref, computed, inject } from 'vue';
import { appointmentState, bookingStatus } from '@/definitions';
import { useUserStore } from '@/stores/user-store';

// eslint-disable-next-line import/prefer-default-export
export const useAppointmentStore = defineStore('appointments', () => {
  const dj = inject('dayjs');

  // State
  const isLoaded = ref(false);

  // Data
  const appointments = ref([]);
  const pendingAppointments = computed(
    () => appointments.value.filter((a) => a.status === bookingStatus.requested),
  );

  /**
   * Append additional data to retrieved appointments
   */
  const postFetchProcess = async () => {
    const userStore = useUserStore();

    appointments.value.forEach((a) => {
      a.active = a.status !== bookingStatus.booked;
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
    isLoaded, appointments, pendingAppointments, postFetchProcess, fetch, $reset,
  };
});
