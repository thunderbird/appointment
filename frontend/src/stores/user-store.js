import { defineStore } from 'pinia';
import { useLocalStorage } from '@vueuse/core';

const initialUserObject = {
  email: null,
  level: null,
  name: null,
  timezone: null,
  username: null,
  signedUrl: null,
  avatarUrl: null,
  accessToken: null,
};

export const useUserStore = defineStore('user', () => {
  const data = useLocalStorage('tba/user', structuredClone(initialUserObject));

  const exists = () => data.value.accessToken !== null;
  const $reset = () => {
    data.value = structuredClone(initialUserObject);
  };

  /**
   * Retrieve the current signed url and update store
   * @param {function} fetch preconfigured API fetch function
   * @return {boolean}
   */
  const updateSignedUrl = async (fetch) => {
    const { error, data: sigData } = await fetch('me/signature').get().json();

    if (error.value || !sigData.value?.url) {
      console.error(error.value, sigData.value);
      return false;
    }

    data.value.signedUrl = sigData.value.url;

    return true;
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
      return false;
    }

    data.value = {
      // Include the previous values first
      ...data.value,
      // Then the new ones!
      username: userData.value.username,
      name: userData.value.name,
      email: userData.value.email,
      level: userData.value.level,
      timezone: userData.value.timezone,
      avatarUrl: userData.value.avatar_url,
    };

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
      console.error(error.value, sigData.value);
      return false;
    }

    return updateSignedUrl(fetch);
  };

  /**
   * Request subscriber login
   * @param {function} fetch preconfigured API fetch function
   * @param {string} username
   * @param {string} password
   * @returns {boolean} true if login was successful
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
        return false;
      }

      data.value.accessToken = tokenData.value.access_token;
    } else if (import.meta.env.VITE_AUTH_SCHEME === 'fxa') {
      // For FXA we re-use the username parameter as our access token
      data.value.accessToken = username;
    } else {
      return false;
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
    data, exists, $reset, updateSignedUrl, profile, changeSignedUrl, login, logout,
  };
});
