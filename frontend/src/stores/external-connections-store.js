import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

const initialData = {
  isInit: false,
  zoom: [],
  fxa: [],
};

// eslint-disable-next-line import/prefer-default-export
export const useExternalConnectionsStore = defineStore('externalConnections', () => {
  const data = ref(structuredClone(initialData));

  const connections = computed(() => data.value);
  const isLoaded = computed(() => data.value.isInit);
  const fxa = computed(() => data.value.fxa ?? []);
  const zoom = computed(() => data.value.zoom ?? []);

  const fetch = async (call) => {
    if (isLoaded.value) {
      return;
    }

    const { data: connectionsData } = await call('account/external-connections').get().json();
    data.value = { ...connectionsData.value, isInit: true };
  };
  const reset = () => data.value = structuredClone(initialData);

  return { data, connections, isLoaded, fxa, zoom, fetch, reset };
});
