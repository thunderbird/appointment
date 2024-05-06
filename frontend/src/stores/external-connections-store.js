import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

// eslint-disable-next-line import/prefer-default-export
export const useExternalConnectionsStore = defineStore('externalConnections', () => {
  // State
  const isLoaded = ref(false);

  // Data
  const zoom = ref([]);
  const fxa = ref([]);
  const google = ref([]);
  const connections = computed(() => ({
    // FXA should be at the top imo
    fxa: fxa.value,
    google: google.value,
    zoom: zoom.value,
  }));

  /**
   * Get all external connections for current user
   * @param {function} call preconfigured API fetch function
   */
  const fetch = async (call) => {
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
