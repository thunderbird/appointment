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

export const useUserStore = defineStore('user', {
  state: () => ({
    data: useLocalStorage('tba/user', structuredClone(initialUserObject)),
  }),
  actions: {
    exists() {
      return this.data.accessToken !== null;
    },
    reset() {
      this.$patch({ data: structuredClone(initialUserObject) });
    },
    async profile(fetch) {
      const { error, data } = await fetch('me').get().json();

      // Failed to get profile data, log this user out and return false
      if (error.value || !data.value) {
        this.reset();
        return false;
      }

      this.$patch({
        data: {
          username: data.value.username,
          name: data.value.name,
          email: data.value.email,
          level: data.value.level,
          timezone: data.value.timezone,
          avatarUrl: data.value.avatar_url,
        }
      });

      return await this.updateSignedUrl(fetch);
    },
    // retrieve the current signed url and update store
    async updateSignedUrl(fetch) {
      const { error, data } = await fetch('me/signature').get().json();

      if (error.value || !data.value.url) {
        console.error(error.value, data.value);
        return false;
      }

      this.data.signedUrl = data.value.url;

      return true;
    },
    // invalidate the current signed url and replace it with a new one
    async changeSignedUrl(fetch) {
      const { error, data } = await fetch('me/signature').post().json();

      if (error.value) {
        console.error(error.value, data.value);
        return false;
      }

      return this.updateSignedUrl(fetch);
    },
    async login(fetch, username, password) {
      this.reset();

      if (import.meta.env.VITE_AUTH_SCHEME === 'password') {
        // fastapi wants us to send this as formdata :|
        const formData = new FormData(document.createElement('form'));
        formData.set('username', username);
        formData.set('password', password);
        const {error, data} = await fetch('token').post(formData).json();

        if (error.value || !data.value.access_token) {
          return false;
        }

        this.data.accessToken = data.value.access_token;
      } else if (import.meta.env.VITE_AUTH_SCHEME === 'fxa') {
        // For FXA we re-use the username parameter as our access token
        this.data.accessToken = username;
      }

      return await this.profile(fetch);
    },
    async logout(fetch) {
      const { error } = await fetch('logout').get().json();

      if (error.value) {
        console.warn("Error logging out: ", error.value);
      }

      this.reset();
    }
  },
});
