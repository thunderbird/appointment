import { defineStore } from 'pinia';
import { UserActivity } from '@/models';
import { useLocalStorage } from '@vueuse/core';
import { Dismissibles } from '@/definitions';

const initialUserActivityObject = {
  dismissedBetaWarning: false,
} as UserActivity;

export const useUserActivityStore = defineStore('user-activity', () => {
  const data = useLocalStorage('tba/user-activity', initialUserActivityObject);

  const dismiss = (dismissible: Dismissibles) => {
    if (dismissible === Dismissibles.BetaWarning) {
      data.value.dismissedBetaWarning = true;
    }
  };

  return { dismiss, data };
});
