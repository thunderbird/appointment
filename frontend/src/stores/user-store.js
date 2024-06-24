import { defineStore } from 'pinia';
import { useLocalStorage } from '@vueuse/core';
import { i18n } from '@/composables/i18n';
import { computed } from 'vue';

const initialUserObject = {
  setup: false,
  email: null,
  preferredEmail: null,
  level: null,
  name: null,
  timezone: null,
  username: null,
  signedUrl: null,
  avatarUrl: null,
  accessToken: null,
  scheduleSlugs: [],
};

export const useUserStore = defineStore('user', () => {
  const data = useLocalStorage('tba/user', structuredClone(initialUserObject));

  const myLink = computed(() => {
    const scheduleSlug = data.value?.scheduleSlugs?.length > 0 ? data.value?.scheduleSlugs[0] : null;
    if (scheduleSlug) {
      return `${import.meta.env.VITE_SHORT_BASE_URL}/${data.value.username}/${scheduleSlug}/`;
    }
    return data.value.signedUrl;
  });

  const exists = () => data.value.accessToken !== null;
  const $reset = () => {
    data.value = structuredClone(initialUserObject);
  };

  const updateProfile = (userData) => {
    data.value = {
      // Include the previous values first
      ...data.value,
      // Then the new ones!
      username: userData.username,
      name: userData.name,
      email: userData.email,
      preferredEmail: userData?.preferred_email ?? userData.email,
      level: userData.level,
      timezone: userData.timezone,
      avatarUrl: userData.avatar_url,
    };
  };

  const updateScheduleUrls = (scheduleData) => {
    data.value = {
      ...data.value,
      scheduleSlugs: scheduleData.map((schedule) => schedule?.slug),
    };
  };

  /**
   * Retrieve the current signed url and update store
   * @param {function} fetch preconfigured API fetch function
   */
  const updateSignedUrl = async (fetch) => {
    const { error, data: sigData } = await fetch('me/signature').get().json();

    if (error.value || !sigData.value?.url) {
      return { error: sigData.value?.detail ?? error.value };
    }

    data.value.signedUrl = sigData.value.url;

    return { error: false };
  };

  const updateUser = async (fetch, inputData) => {
    const { data: userData, error } = await fetch('me').put(inputData).json();
    if (!error.value) {
      // update user in store
      await updateProfile(userData.value);
      await updateSignedUrl(fetch);

      return { error: false };
    }

    return { error: data.value ?? error.value };
  };

  /**
   * Update store with profile data from db
   * @param {function} fetch preconfigured API fetch function
   * @return {boolean}
   */
  const profile = async (fetch) => {
    const { error, data: userData } = await fetch('me').get().json();

    // Failed to get profile data, log this user out and return false
    if (error.value || !userData.value) {
      $reset();
      return { error: userData.value?.detail ?? error.value };
    }

    updateProfile(userData.value);

    return updateSignedUrl(fetch);
  };

  /**
   * Invalidate the current signed url and replace it with a new one
   * @param {function} fetch preconfigured API fetch function
   * @return {boolean}
   */
  const changeSignedUrl = async (fetch) => {
    const { error, data: sigData } = await fetch('me/signature').post().json();

    if (error.value) {
      return { error: sigData.value?.detail ?? error.value };
    }

    return updateSignedUrl(fetch);
  };

  /**
   * Request subscriber login
   * @param {function} fetch preconfigured API fetch function
   * @param {string} username
   * @param {string|null} password or null if fxa authentication
   * @returns {Promise<boolean>} true if login was successful
   */
  const login = async (fetch, username, password) => {
    $reset();

    if (import.meta.env.VITE_AUTH_SCHEME === 'password') {
      // fastapi wants us to send this as formdata :|
      const formData = new FormData(document.createElement('form'));
      formData.set('username', username);
      formData.set('password', password);
      const { error, data: tokenData } = await fetch('token').post(formData).json();

      if (error.value || !tokenData.value.access_token) {
        return { error: tokenData.value?.detail ?? error.value };
      }

      data.value.accessToken = tokenData.value.access_token;
    } else if (import.meta.env.VITE_AUTH_SCHEME === 'fxa') {
      // For FXA we re-use the username parameter as our access token
      data.value.accessToken = username;
    } else {
      return { error: i18n.t('error.loginMethodNotSupported') };
    }

    return profile(fetch);
  };

  /**
   * Do subscriber logout and reset store
   * @param {function} fetch preconfigured API fetch function
   */
  const logout = async (fetch) => {
    const { error } = await fetch('logout').get().json();

    if (error.value) {
      // TODO: show error message
      console.warn('Error logging out: ', error.value);
    }

    $reset();
  };

  return {
    data, exists, $reset, updateSignedUrl, profile, updateProfile, changeSignedUrl, login, logout, myLink, updateScheduleUrls, updateUser,
  };
});
