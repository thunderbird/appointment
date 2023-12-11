import { defineStore } from 'pinia';
import { appointmentState } from '@/definitions';
import { useUserStore } from '@/stores/user-store';
import dj from 'dayjs';

const initialData = {
  appointments: [],
  isInit: false,
};

// eslint-disable-next-line import/prefer-default-export
export const useAppointmentStore = defineStore('appointments', {
  state: () => ({
    data: structuredClone(initialData),
  }),
  getters: {
    isLoaded() {
      return this.data.isInit;
    },
    appointments() {
      return this.data.appointments;
    },
    pendingAppointments() {
      return this.data.appointments.filter((a) => a.status === appointmentState.pending);
    },
  },
  actions: {
    status(appointment) {
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
    },
    reset() {
      this.$patch({ data: structuredClone(initialData) });
    },
    async mergeCalendarInfo(calendarsById) {
      const userStore = useUserStore();

      this.data.appointments.forEach((a) => {
        a.calendar_title = calendarsById[a.calendar_id]?.title;
        a.calendar_color = calendarsById[a.calendar_id]?.color;
        a.status = this.status(a);
        a.active = a.status !== appointmentState.past; // TODO
        // convert start dates from UTC back to users timezone
        a.slots.forEach((s) => {
          s.start = dj.utc(s.start).tz(userStore.data.timezone ?? dj.tz.guess());
        });
      });
    },
    async fetch(call) {
      const { data, error } = await call('me/appointments').get().json();
      if (!error.value) {
        if (data.value === null || typeof data.value === 'undefined') return;
        this.data.appointments = data.value;
        this.data.isInit = true;
      }
    },
  },
});
