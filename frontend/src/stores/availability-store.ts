import { computed, ref, toRefs } from "vue";
import { defineStore } from "pinia";
import { Fetch } from "@/models";
import { deepClone } from "@/utils";

import { createCalendarStore } from "./calendar-store";
import { createUserStore } from "./user-store";
import { createScheduleStore } from "./schedule-store";
import { createExternalConnectionsStore } from "./external-connections-store";

export const useAvailabilityStore = defineStore('availability', () => {
  // Refs
  const call = ref(null);
  const isLoaded = ref(false);

  const initialState: any = ref({}); // TODO: Update type
  const currentState: any = ref({}); // TODO: Update type

  const isDirty = computed(() => (
    JSON.stringify(initialState.value) !== JSON.stringify(currentState.value)
  ))

  /**
   * Initialize store with data required at runtime
   *
   * @param fetch preconfigured function to perform API calls
   */
  const init = async (fetch: Fetch) => {
    call.value = fetch;

    const userStore = createUserStore(fetch);
    const calendarStore = createCalendarStore(fetch);
    const scheduleStore = createScheduleStore(fetch);
    const externalConnectionStore = createExternalConnectionsStore(fetch);

    const { isLoaded: isCalendarStoreLoaded, connectedCalendars } = toRefs(calendarStore);
    const { isLoaded: isExternalConnectionStoreLoaded } = toRefs(externalConnectionStore);
    const { isLoaded: isScheduleStoreLoaded, firstSchedule } = toRefs(scheduleStore);

    // First, let's make sure that all stores are loaded
    // so that we can initialize the currentState properly
    if (!isCalendarStoreLoaded.value) {
      await calendarStore.fetch();
    }

    if (!isExternalConnectionStoreLoaded.value) {
      await externalConnectionStore.fetch();
    }

    if (!isScheduleStoreLoaded.value) {
      await scheduleStore.fetch();
    }

    if (firstSchedule.value) {
      initialState.value = firstSchedule.value;

      // calculate utc back to user timezone
      initialState.value.start_time = scheduleStore.timeToFrontendTime(initialState.value.start_time, initialState.value.time_updated);
      initialState.value.end_time = scheduleStore.timeToFrontendTime(initialState.value.end_time, initialState.value.time_updated);
      initialState.value.availabilities?.forEach((a, i) => {
        initialState.value.availabilities[i].start_time = scheduleStore.timeToFrontendTime(a.start_time, initialState.value.time_updated);
        initialState.value.availabilities[i].end_time = scheduleStore.timeToFrontendTime(a.end_time, initialState.value.time_updated);
      });

      // Adjust the default calendar if the one attached is not connected.
      const { calendar_id: calendarId } = initialState.value;

      const calendar = connectedCalendars.value.find((cal) => cal.id === calendarId);
      if (!calendar || !calendar.connected) {
        initialState.value.calendar_id = connectedCalendars.value[0].id;
      }
    }

    // Booking Page Link data
    initialState.value.link_slug = userStore.mySlug;

    // Copy initialState
    currentState.value = deepClone({ ...initialState.value }); 

    isLoaded.value = true;
  }

  const saveChanges = async () => {
    console.log("Object to be saved:", currentState.value);
  }

  const revertChanges = () => {
    currentState.value = deepClone({ ...initialState.value }); 
  }

  return {
    init,
    isLoaded,
    isDirty,
    initialState,
    currentState,
    saveChanges,
    revertChanges,
  }
});

export const createAvailabilityStore = (call: Fetch) => {
  const store = useAvailabilityStore();
  store.init(call);
  return store;
};
