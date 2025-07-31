import { computed, inject, ref } from "vue";
import { defineStore, storeToRefs } from "pinia";
import { Fetch, Schedule } from "@/models";
import { DateFormatStrings, DEFAULT_SLOT_DURATION, EventLocationType, MeetingLinkProviderType } from "@/definitions";
import { dayjsKey } from '@/keys';

import { useCalendarStore } from "./calendar-store";
import { useUserStore } from "./user-store";
import { useScheduleStore } from "./schedule-store";
import { useExternalConnectionsStore } from "./external-connections-store";
import { deepClone } from "@/utils";

export const useAvailabilityStore = defineStore('appointments', () => {
  const dj = inject(dayjsKey);

  const userStore = useUserStore();
  const calendarStore = useCalendarStore();
  const scheduleStore = useScheduleStore();
  const externalConnectionStore = useExternalConnectionsStore();

  const { connectedCalendars } = storeToRefs(calendarStore);
  const { firstSchedule } = storeToRefs(scheduleStore);

  console.log(connectedCalendars);

  const initialState: Schedule = {
    active: calendarStore.hasConnectedCalendars,
    name: `${userStore.data.name}'s Availability`,
    calendar_id: connectedCalendars.value[0].id,
    location_type: EventLocationType.InPerson,
    location_url: '',
    details: '',
    start_date: dj().format(DateFormatStrings.QalendarFullDay),
    end_date: null,
    start_time: '09:00',
    end_time: '17:00',
    earliest_booking: 1440,
    farthest_booking: 20160,
    weekdays: [1, 2, 3, 4, 5],
    slot_duration: DEFAULT_SLOT_DURATION,
    meeting_link_provider: MeetingLinkProviderType.None,
    slug: userStore.mySlug,
    booking_confirmation: true,
    availabilities: [],
    use_custom_availabilities: false,
  };

  // Refs
  const call = ref(null);
  const currentState = ref({ ...initialState });
  const isLoaded = ref(false);

  // Computed properties
  const shouldGenerateZoomLink = computed(() => currentState.value.meeting_link_provider === MeetingLinkProviderType.Zoom);
  const isFormDirty = computed(
    () => JSON.stringify(initialState) !== JSON.stringify(currentState.value),
  );

  /**
   * Initialize helper stores if not initialized yet
   * userStore doesn't have to be checked as it is already pre-loaded
   */
  const initializeHelperStores = async () => {
    if (!calendarStore.isLoaded) {
      await calendarStore.fetch();
    }

    if (!scheduleStore.isLoaded) {
      await scheduleStore.fetch();
    }

    if (!externalConnectionStore.isLoaded) {
      await externalConnectionStore.fetch();
    }
  }

  /**
   * Initialize store with data required at runtime
   *
   * @param fetch preconfigured function to perform API calls
   */
  const init = async (fetch: Fetch) => {
    call.value = fetch;

    console.log("1");

    await initializeHelperStores();

    console.log("2");

    if (firstSchedule) {
      currentState.value = deepClone({ ...firstSchedule });

      // calculate utc back to user timezone
      currentState.value.start_time = scheduleStore.timeToFrontendTime(currentState.value.start_time, currentState.value.time_updated);
      currentState.value.end_time = scheduleStore.timeToFrontendTime(currentState.value.end_time, currentState.value.time_updated);
      currentState.value.availabilities?.forEach((a, i) => {
        currentState.value.availabilities[i].start_time = scheduleStore.timeToFrontendTime(a.start_time, currentState.value.time_updated);
        currentState.value.availabilities[i].end_time = scheduleStore.timeToFrontendTime(a.end_time, currentState.value.time_updated);
      });

      // Adjust the default calendar if the one attached is not connected.
      const { calendar_id: calendarId } = currentState.value;

      const calendar = connectedCalendars.value.find((cal) => cal.id === calendarId);
      if (!calendar || !calendar.connected) {
        currentState.value.calendar_id = connectedCalendars.value[0].id;
      }
    }

    console.log("3");

    isLoaded.value = true;
  }

  return {
    init,
    initialState,
    isLoaded,
    firstSchedule,
    connectedCalendars,
    shouldGenerateZoomLink,
    isFormDirty,
  }
});

export const createAvailabilityStore = (call: Fetch) => {
  const store = useAvailabilityStore();
  store.init(call);
  return store;
};
