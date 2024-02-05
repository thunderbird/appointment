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
  const reset = () => data.value = structuredClone(initialUserObject);

  // retrieve the current signed url and update store
  const updateSignedUrl = async (fetch) => {
    const { error, data: sigData } = await fetch('me/signature').get().json();

    if (error.value || !sigData.value?.url) {
      console.error(error.value, sigData.value);
      return false;
    }

    data.value.signedUrl = sigData.value.url;

    return true;
  };

  // update store with profile data from db
  const profile = async (fetch) => {
    const { error, data: userData } = await fetch('me').get().json();

    // Failed to get profile data, log this user out and return false
    if (error.value || !userData.value) {
      reset();
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

    return await updateSignedUrl(fetch);
  };

  // invalidate the current signed url and replace it with a new one
  const changeSignedUrl = async (fetch) => {
    const { error, data: sigData } = await fetch('me/signature').post().json();

    if (error.value) {
      console.error(error.value, sigData.value);
      return false;
    }

    return await updateSignedUrl(fetch);
  };

  const login = async (fetch, username, password) => {
    reset();

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

    return await profile(fetch);
  };

  const logout = async (fetch) => {
    const { error } = await fetch('logout').get().json();

    if (error.value) {
      console.warn('Error logging out: ', error.value);
    }

    reset();
  };

  return {
    data, exists, reset, updateSignedUrl, profile, changeSignedUrl, login, logout,
  };
});
