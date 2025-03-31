import { defineStore } from 'pinia';
import { ref } from 'vue';

 
export const useSiteNotificationStore = defineStore('siteNotification', () => {
  // State
  const isVisible = ref(false);

  // Data
  const id = ref(null);
  const title = ref('');
  const actionUrl = ref('');
  const message = ref('');

  /**
   * Check a given id if it is currently locked
   * @param checkId notification id to check agains current id
   */
  const isSame = (checkId: string) => id.value === checkId;

  /**
   * Lock the given id
   * @param lockId notification id to lock in
   */
  const lock = (lockId: string) => { id.value = lockId; };

  /**
   * Make a notification with given configuration appear
   * @param showId notification identifier
   * @param showTitle notification title
   * @param showMessage notification message
   * @param showActionUrl target url if notification should be a link
   */
  const show = (showId: string, showTitle: string, showMessage: string, showActionUrl: string) => {
    isVisible.value = true;
    id.value = showId;
    title.value = showTitle;
    actionUrl.value = showActionUrl;
    message.value = showMessage;
  };

  /**
   * Restore default state, hide and unlock notification
   */
  const $reset = () => {
    isVisible.value = false;
    id.value = null;
    title.value = '';
    actionUrl.value = '';
    message.value = '';
  };

  return {
    isVisible, title, actionUrl, message, isSame, lock, show, $reset,
  };
});
