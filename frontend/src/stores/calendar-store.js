import { defineStore } from 'pinia';

const initialData = {
  calendars: [],
  isInit: false,
};

// eslint-disable-next-line import/prefer-default-export
export const useCalendarStore = defineStore('calendars', {
  state: () => ({
    data: structuredClone(initialData),
  }),
  getters: {
    isLoaded() {
      return this.data.isInit;
    },
    unconnectedCalendars() {
      return this.data.calendars.filter((cal) => !cal.connected);
    },
    connectedCalendars() {
      return this.data.calendars.filter((cal) => cal.connected);
    },
    allCalendars() {
      return this.data.calendars;
    },
  },
  actions: {
    reset() {
      this.$patch({ data: structuredClone(initialData) });
    },
    async fetch(call) {
      if (this.isLoaded) {
        return;
      }

      const { data, error } = await call('me/calendars?only_connected=false').get().json();
      if (!error.value) {
        if (data.value === null || typeof data.value === 'undefined') return;
        this.data.calendars = data.value;
        this.data.isInit = true;
      }
    },
  },
});
