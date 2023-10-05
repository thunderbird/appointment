import { defineStore } from 'pinia';
import { useLocalStorage } from '@vueuse/core';

const initialUserObject = {
  email: null,
  level: null,
  name: null,
  timezone: null,
  username: null,
};

export const useUserStore = defineStore('user', {
  state: () => ({
    data: useLocalStorage('tba/user', initialUserObject),
  }),
  actions: {
    exists() {
      return this.data.email !== null;
    },
    reset() {
      this.$patch({ data: initialUserObject });
    },
  },
});
