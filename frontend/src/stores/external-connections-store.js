import { defineStore } from 'pinia';

const initialData = {
  zoom: [],
  fxa: [],
  isInit: false,
};

// eslint-disable-next-line import/prefer-default-export
export const useExternalConnectionsStore = defineStore('externalConnections', {
  state: () => ({
    data: structuredClone(initialData),
  }),
  getters: {
    isLoaded() {
      return this.data.isInit;
    },
    connections() {
      return this.data;
    },
    fxa() {
      return this.data.fxa ?? [];
    },
    zoom() {
      return this.data.zoom ?? [];
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

      const { data } = await call('account/external-connections').get().json();
      this.$patch({ data: { ...data.value, isInit: true } });
    },
  },
});
