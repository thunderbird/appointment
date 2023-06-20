import { ref } from 'vue';

// eslint-disable-next-line import/prefer-default-export
export const siteNotificationStore = ref({
  // Ensure we don't need to set the same notification twice
  id: null,
  // Details
  display: false,
  title: '',
  message: '',
  actionUrl: '',
});
