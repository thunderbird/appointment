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

  /**
   * Check a given id if it is currently locked
   * @param {string} checkId notification id to check agains current id
   * @returns {boolean}
   */
  const isSame = (checkId) => id.value === checkId;

  /**
   * Lock the given id
   * @param {string} lockId notification id to lock in
   */
  const lock = (lockId) => id.value = lockId;

  /**
   * Make a notification with given configuration appear
   * @param {string} showId notification identifier
   * @param {string} showTitle notification title
   * @param {string} showMessage notification message
   * @param {string} showActionUrl target url if notification should be a link
   */
  const show = (showId, showTitle, showMessage, showActionUrl) => {
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

  return { isVisible, title, actionUrl, message, isSame, lock, show, $reset };
});
