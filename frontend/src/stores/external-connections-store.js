import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

// eslint-disable-next-line import/prefer-default-export
export const useExternalConnectionsStore = defineStore('externalConnections', () => {
  // State
  const isLoaded = ref(false);

  // Data
  const zoom = ref([]);
  const fxa = ref([]);
  const connections = computed(() => ({
    zoom: zoom.value,
    fxa: fxa.value,
  }));

  // Get all external connections for current user
  const fetch = async (call) => {
    if (isLoaded.value) {
      return;
    }

    const { data } = await call('account/external-connections').get().json();
    zoom.value = data.value?.zoom ?? [];
    fxa.value = data.value?.fxa ?? [];
    isLoaded.value = true;
  };

  const $reset = () => {
    zoom.value = [];
    fxa.value = [];
    isLoaded.value = false;
  };

  return { connections, isLoaded, fxa, zoom, fetch, $reset };
});
