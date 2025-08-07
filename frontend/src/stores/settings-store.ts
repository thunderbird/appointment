import { computed, ref, toRefs } from "vue";
import { defineStore } from "pinia";
import { Fetch, SettingsForm } from "@/models";
import { deepClone } from "@/utils";

import { createCalendarStore } from "./calendar-store";
import { createUserStore } from "./user-store";
import { createExternalConnectionsStore } from "./external-connections-store";

export const useSettingsStore = defineStore('settings', () => {
  const call = ref(null);
  const isLoaded = ref(false);

  const initialState = ref<SettingsForm>({});
  const currentState = ref<SettingsForm>({});

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
    const externalConnectionStore = createExternalConnectionsStore(fetch);

    const { isLoaded: isCalendarStoreLoaded } = toRefs(calendarStore);
    const { isLoaded: isExternalConnectionStoreLoaded } = toRefs(externalConnectionStore);

    // First, let's make sure that all stores are loaded
    // so that we can initialize the currentState properly
    if (!isCalendarStoreLoaded.value) {
      await calendarStore.fetch();
    }

    if (!isExternalConnectionStoreLoaded.value) {
      await externalConnectionStore.fetch();
    }

    // Preferences section
    initialState.value.colourScheme = userStore.data.settings.colourScheme;
    initialState.value.language = userStore.data.settings.language;
    initialState.value.startOfWeek = userStore.data.settings.startOfWeek;
    initialState.value.timeFormat = userStore.data.settings.timeFormat;

    // Copy initialState
    currentState.value = deepClone({ ...initialState.value }); 

    isLoaded.value = true;
  }

  const revertChanges = () => {
    currentState.value = deepClone({ ...initialState.value }); 
  }

  const connectZoom = async () => {
    const { data } = await call.value('zoom/auth').get().json();

    // Ship them to the auth link
    window.location.href = data.value.url;
  }
  
  const $reset = async () => {
    isLoaded.value = false;

    await init(call.value);
  }

  return {
    init,
    isLoaded,
    isDirty,
    initialState,
    currentState,
    connectZoom,
    revertChanges,
    $reset,
  }
});

export const createSettingsStore = (call: Fetch) => {
  const store = useSettingsStore();
  store.init(call);
  return store;
};
