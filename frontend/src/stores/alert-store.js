import { defineStore } from 'pinia';
import { ref } from 'vue';

// eslint-disable-next-line import/prefer-default-export
export const useSiteNotificationStore = defineStore('siteNotification', () => {
  // State
  const isVisible = ref(false);

  // Data
  const id = ref(null);
  const title = ref('');
  const actionUrl = ref('');
  const message = ref('');

  const isSame = (checkId) => id.value === checkId;

  const lock = (lockId) => id.value = lockId;

  const show = (showId, showTitle, showMessage, showActionUrl) => {
    isVisible.value = true;
    id.value = showId;
    title.value = showTitle;
    actionUrl.value = showActionUrl;
    message.value = showMessage;
  };

  const reset = () => {
    isVisible.value = false;
    id.value = null;
    title.value = '';
    actionUrl.value = '';
    message.value = '';
  };

  return { isVisible, title, actionUrl, message, isSame, lock, show, reset };
});
