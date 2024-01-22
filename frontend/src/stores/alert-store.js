import { ref, computed } from 'vue';
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
export const useSiteNotificationStore = defineStore('siteNotification', () => {
  const data = ref(structuredClone(initialSiteNotificationObject));

  const isVisible = computed(() => data.value.display);
  const title = computed(() => data.value.title);
  const actionUrl = computed(() => data.value.actionUrl);
  const message = computed(() => data.value.message);

  const isSameNotification = (id) => data.value.id === id;
  const lock = (id) => data.value.id = id;
  const show = (id, title, message, actionUrl) => {
    data.value = {
      id,
      display: true,
      title,
      message,
      actionUrl,
    };
  };
  const reset = () => data.value = structuredClone(initialSiteNotificationObject);

  return { data, isVisible, title, actionUrl, message, isSameNotification, lock, show, reset };
});
