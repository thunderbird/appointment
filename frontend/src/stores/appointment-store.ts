import { Dayjs, ConfigType } from 'dayjs';
import { defineStore } from 'pinia';
import { ref, computed, inject } from 'vue';
import { bookingStatus } from '@/definitions';
import { useUserStore } from '@/stores/user-store';
import {
  Appointment, AppointmentListResponse, Fetch, Slot,
} from '@/models';
import { dayjsKey } from '@/keys';

// eslint-disable-next-line import/prefer-default-export
export const useAppointmentStore = defineStore('appointments', () => {
  const dj = inject(dayjsKey);
  const tzGuess = inject<string>('tzGuess');

  // State
  const isLoaded = ref(false);

  // Data
  const appointments = ref<Appointment[]>([]);
  const pendingAppointments = computed(
    (): Appointment[] => appointments.value.filter((a) => a?.slots[0]?.booking_status === bookingStatus.requested),
  );
  const pendingFutureAppointments = computed(
    (): Appointment[] => pendingAppointments.value.filter((a) => a?.slots[0]?.start > dj()),
  );

  /**
   * Append additional data to retrieved appointments
   */
  const postFetchProcess = async () => {
    const userStore = useUserStore();

    appointments.value.forEach((a) => {
      a.active = a.status !== bookingStatus.booked;
      // convert start dates from UTC back to users timezone
      a.slots.forEach((s: Slot) => {
        s.start = dj(s.start).utc(true).tz(userStore.data.timezone ?? tzGuess);
      });
    });
  };

  /**
   * Get all appointments for current user
   * @param call preconfigured API fetch function
   */
  const fetch = async (call: Fetch) => {
    const { data, error }: AppointmentListResponse = await call('me/appointments').get().json();
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
    isLoaded, appointments, pendingAppointments, pendingFutureAppointments, postFetchProcess, fetch, $reset,
  };
});
