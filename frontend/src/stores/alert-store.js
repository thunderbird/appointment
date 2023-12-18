import { defineStore } from 'pinia';

const initialSiteNotificationObject = {
  // Ensure we don't need to set the same notification twice
  id: null,
  // Details
  display: false,
  title: '',
  message: '',
  actionUrl: '',
};

// eslint-disable-next-line import/prefer-default-export
export const useSiteNotificationStore = defineStore('siteNotification', {
  state: () => ({
    data: structuredClone(initialSiteNotificationObject),
  }),
  getters: {
    isVisible() {
      return this.data.display;
    },
    title() {
      return this.data.title;
    },
    actionUrl() {
      return this.data.actionUrl;
    },
    message() {
      return this.data.message;
    },
  },
  actions: {
    isSameNotification(id) {
      return this.data.id === id;
    },
    lock(id) {
      this.$patch({
        data: { id },
      });
    },
    show(id, title, message, actionUrl) {
      this.$patch({
        data: {
          id,
          display: true,
          title,
          message,
          actionUrl,
        },
      });
    },
    reset() {
      this.$patch({ data: structuredClone(initialSiteNotificationObject) });
    },
  },
});
