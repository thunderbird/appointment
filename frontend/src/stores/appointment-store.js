import { defineStore } from 'pinia';
import { ref, computed, inject } from 'vue';
import { appointmentState } from '@/definitions';
import { useUserStore } from '@/stores/user-store';

const initialData = {
  appointments: [],
  isInit: false,
};

// eslint-disable-next-line import/prefer-default-export
export const useAppointmentStore = defineStore('appointments', () => {
  // TODO: needs to be provided somehow in the testing file
  const dj = inject('dayjs');

  const data = ref(structuredClone(initialData));

  const isLoaded = computed(() => data.value.isInit);
  const appointments = computed(() => data.value.appointments);
  const pendingAppointments = computed(
    () => data.value.appointments.filter((a) => a.status === appointmentState.pending)
  );

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
  const postFetchProcess = async () => {
    const userStore = useUserStore();

    data.value.appointments.forEach((a) => {
      a.status = status(a);
      a.active = a.status !== appointmentState.past; // TODO
      // convert start dates from UTC back to users timezone
      a.slots.forEach((s) => {
        s.start = dj.utc(s.start).tz(userStore.data.timezone ?? dj.tz.guess());
      });
    });
  };
  const fetch = async (call) => {
    const { data: apmtData, error } = await call('me/appointments').get().json();
    if (!error.value) {
      if (apmtData.value === null || typeof apmtData.value === 'undefined') return;
      data.value.appointments = apmtData.value;
      data.value.isInit = true;
    }
    // After we fetch the data, apply some processing
    await postFetchProcess();
  };
  const reset = () => data.value = structuredClone(initialData);

  return { data, isLoaded, appointments, pendingAppointments, status, postFetchProcess, fetch, reset };
});
