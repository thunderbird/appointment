import { ExternalConnection, ExternalConnectionCollection, FetchExternalConnectionCollection } from '@/models';
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

// eslint-disable-next-line import/prefer-default-export
export const useExternalConnectionsStore = defineStore('externalConnections', () => {
  // State
  const isLoaded = ref(false);

  // Data
  const zoom = ref<ExternalConnection[]>([]);
  const fxa = ref<ExternalConnection[]>([]);
  const google = ref<ExternalConnection[]>([]);
  const connections = computed((): ExternalConnectionCollection => ({
    // FXA should be at the top since it represents the Appointment subscriber.
    fxa: fxa.value,
    google: google.value,
    zoom: zoom.value,
  }));

  /**
   * Get all external connections for current user
   * @param call preconfigured API fetch function
   */
  const fetch = async (call: FetchExternalConnectionCollection) => {
    if (isLoaded.value) {
      return;
    }

    const { data } = await call('account/external-connections').get().json();
    zoom.value = data.value?.zoom ?? [];
    fxa.value = data.value?.fxa ?? [];
    google.value = data.value?.google ?? [];
    isLoaded.value = true;
  };

  /**
   * Restore default state, empty and unload connections
   */
  const $reset = () => {
    zoom.value = [];
    fxa.value = [];
    google.value = [];
    isLoaded.value = false;
  };

  return {
    connections, isLoaded, fxa, zoom, google, fetch, $reset,
  };
});
