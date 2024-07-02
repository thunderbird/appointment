import {ExternalConnection, ExternalConnectionCollection, Fetch, ExternalConnectionCollectionResponse} from '@/models';
import {defineStore} from 'pinia';
import {ref, computed} from 'vue';
import {useRouter} from "vue-router";

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
  const fetch = async (call: Fetch) => {
    if (isLoaded.value) {
      return;
    }

    const {data}: ExternalConnectionCollectionResponse = await call('account/external-connections').get().json();
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

  const connect = async (call: Fetch, category: string, router: any) => {
    if (category === 'zoom') {
      const {data} = await call('zoom/auth').get().json();
      // Ship them to the auth link
      window.location.href = data.value.url;
    } else if (category === 'google') {
      await router.push('/settings/calendar');
    }
  };

  const disconnect = async (call: Fetch, category: string) => {
    if (category === 'zoom') {
      return call('zoom/disconnect').post();
    } else if (category === 'google') {
      return call('google/disconnect').post();
    }

    return null;
  }

  return {
    connections, isLoaded, fxa, zoom, google, fetch, $reset, connect, disconnect
  };
});
