import { defineStore } from 'pinia';
import { UserActivity } from '@/models';
import { useLocalStorage } from '@vueuse/core';
import { Dismissibles } from '@/definitions';

const initialUserActivityObject = {
  dismissedBetaWarning: false,
} as UserActivity;

/**
 * A place to store the state of UI elements, like a dismissible message or if we want something to stay minimized.
 */
export const useUserActivityStore = defineStore('user-activity', () => {
  const data = useLocalStorage('tba/user-activity', initialUserActivityObject);

  const dismiss = (dismissible: Dismissibles) => {
    if (dismissible === Dismissibles.BetaWarning) {
      data.value.dismissedBetaWarning = true;
    }
  };

  return { dismiss, data };
});
