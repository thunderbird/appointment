import { defineStore } from 'pinia';
import { useLocalStorage } from '@vueuse/core';

const initialUserObject = {
  email: null,
  level: null,
  name: null,
  timezone: null,
  username: null,
  accessToken: null,
};

export const useUserStore = defineStore('user', {
  state: () => ({
    data: useLocalStorage('tba/user', initialUserObject),
  }),
  actions: {
    exists() {
      return this.data.accessToken !== null;
    },
    reset() {
      this.$patch({ data: initialUserObject });
    },
    async profile(fetch) {
      const { error, data } = await fetch('me').get().json();

      // Failed to get profile data, log this user out and return false
      if (error.value) {
        this.reset();
        return false;
      }

      this.$patch({
        data: {
          username: data.value.username,
          name: data.value.name,
          email: data.value.email,
          level: data.value.level,
          timezone: data.value.timezone
        }
      });

      return true;
    },
    async login(fetch, username, password) {
      this.reset();

      // fastapi wants us to send this as formdata :|
      const formData = new FormData(document.createElement('form'));
      formData.set('username', username);
      formData.set('password', password);
      const {error, data} = await fetch('token').post(formData).json();

      if (!data.value.access_token) {
        return false;
      }

      this.data.accessToken = data.value.access_token;

      return await this.profile(fetch);
    }
  },
});
