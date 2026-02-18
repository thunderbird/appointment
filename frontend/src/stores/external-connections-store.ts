import {
  ExternalConnection, ExternalConnectionCollection, ExternalConnectionCollectionResponse, Fetch,
} from '@/models';
import { ExternalConnectionProviders } from '@/definitions';
import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

 
export const useExternalConnectionsStore = defineStore('externalConnections', () => {
  // State
  const isLoaded = ref(false);

  // Data
  const oidc = ref<ExternalConnection[]>([]);
  const zoom = ref<ExternalConnection[]>([]);
  const fxa = ref<ExternalConnection[]>([]);
  const google = ref<ExternalConnection[]>([]);
  const caldav = ref<ExternalConnection[]>([]);
  const connections = computed((): ExternalConnectionCollection => ({
    // FXA should be at the top since it represents the Appointment subscriber.
    oidc: oidc.value,
    fxa: fxa.value,
    google: google.value,
    zoom: zoom.value,
    caldav: caldav.value,
  }));

  /**
   * Whether any checkable external connection (zoom, google, caldav) has an error status.
   */
  const hasUnhealthyConnections = computed((): boolean => {
    const checkable = [...zoom.value, ...google.value, ...caldav.value];
    return checkable.some((ec) => ec.status === 'error');
  });

  const call = ref(null);

  /**
   * Initialize store with data required at runtime
   *
   * @param fetch preconfigured function to perform API calls
   */
  const init = (fetch: Fetch) => {
    call.value = fetch;
  }

  /**
   * Get all external connections for current user
   * @param force
   */
  const fetch = async (force = false) => {
    if (isLoaded.value && !force) {
      return;
    }

    const { data }: ExternalConnectionCollectionResponse = await call.value('account/external-connections').get().json();

    oidc.value = data.value?.oidc ?? [];
    zoom.value = data.value?.zoom ?? [];
    fxa.value = data.value?.fxa ?? [];
    google.value = data.value?.google ?? [];
    caldav.value = data.value?.caldav ?? [];
    isLoaded.value = true;
  };

  /**
   * Restore default state, empty and unload connections
   */
  const $reset = () => {
    oidc.value = [];
    zoom.value = [];
    fxa.value = [];
    google.value = [];
    caldav.value = [];
    isLoaded.value = false;
  };

  const connect = async (provider: ExternalConnectionProviders, router: any) => {
    if (provider === ExternalConnectionProviders.Zoom) {
      const { data } = await call.value('zoom/auth').get().json(); // FIXME: Add type
      // Ship them to the auth link
      window.location.href = data.value.url;
    } else if (provider === ExternalConnectionProviders.Google) {
      await router.push('/settings/calendar');
    }
    // CalDAV is handled in the modal
  };

  /**
   * Run health checks on external connections (zoom, google, caldav).
   * Updates the store with the latest connection statuses from the server.
   */
  const checkStatus = async () => {
    const { data }: ExternalConnectionCollectionResponse = await call.value('account/external-connections/check-status').post().json();

    if (data.value) {
      oidc.value = data.value?.oidc ?? oidc.value;
      zoom.value = data.value?.zoom ?? zoom.value;
      fxa.value = data.value?.fxa ?? fxa.value;
      google.value = data.value?.google ?? google.value;
      caldav.value = data.value?.caldav ?? caldav.value;
      isLoaded.value = true;
    }
  };

  const disconnect = async (provider: ExternalConnectionProviders, typeId: string | null = null) => {
    if (provider === ExternalConnectionProviders.Zoom) {
      return call.value('zoom/disconnect').post();
    }
    if (provider === ExternalConnectionProviders.Google) {
      return call.value('google/disconnect').post({
        type_id: typeId,
      });
    }
    if (provider === ExternalConnectionProviders.Caldav) {
      return call.value('caldav/disconnect').post({
        type_id: typeId,
      });
    }

    return null;
  };

  return {
    connections,
    isLoaded,
    hasUnhealthyConnections,
    oidc,
    fxa,
    zoom,
    google,
    init,
    fetch,
    checkStatus,
    $reset,
    connect,
    disconnect,
  };
});


export const createExternalConnectionsStore = (call: Fetch) => {
  const store = useExternalConnectionsStore();
  store.init(call);
  return store;
};
