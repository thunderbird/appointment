import { defineStore } from 'pinia';
import { ref, computed, defineAsyncComponent } from 'vue';
import { useLocalStorage } from '@vueuse/core';
import { ftueStep } from '@/definitions';

const initialObject = {
  // First step
  step: ftueStep.setupProfile,
  previousStep: ftueStep.setupProfile,
  nextStep: ftueStep.googlePermissions,
};

// eslint-disable-next-line import/prefer-default-export
export const useFTUEStore = defineStore('FTUE', () => {
  // State
  const data = useLocalStorage('tba/ftue', structuredClone(initialObject));

  const stepList = {
    [ftueStep.setupProfile]: {
      previous: null,
      next: ftueStep.googlePermissions,
      title: 'Setup your profile',
      component: defineAsyncComponent({
        loader: () => import('@/components/FTUE/SetupProfile.vue'),
      }),
    },
    [ftueStep.googlePermissions]: {
      previous: ftueStep.setupProfile,
      next: ftueStep.connectCalendars,
      title: 'Allow Google Calendar permissions',
      component: defineAsyncComponent({
        loader: () => import('@/components/FTUE/GooglePermissions.vue'),
      }),
    },
    [ftueStep.connectCalendars]: {
      previous: ftueStep.googlePermissions,
      next: ftueStep.setupSchedule,
      title: 'Connect calendars',
      component: defineAsyncComponent({
        loader: () => import('@/components/FTUE/GooglePermissions.vue'),
      }),
    },
    [ftueStep.setupSchedule]: {
      previous: ftueStep.connectCalendars,
      next: ftueStep.connectVideoConferencing,
      title: 'Create schedule',
      component: defineAsyncComponent({
        loader: () => import('@/components/FTUE/GooglePermissions.vue'),
      }),
    },
    [ftueStep.connectVideoConferencing]: {
      previous: ftueStep.setupSchedule,
      next: ftueStep.finish,
      title: 'Connect video',
      component: defineAsyncComponent({
        loader: () => import('@/components/FTUE/GooglePermissions.vue'),
      }),
    },
    [ftueStep.finish]: {
      previous: ftueStep.connectVideoConferencing,
      next: null,
      title: 'You are set to go!',
      component: defineAsyncComponent({
        loader: () => import('@/components/FTUE/GooglePermissions.vue'),
      }),
    },
  };

  const ftueView = computed(() => {
    if (!stepList[data.value.step]) {
      // This should be an error component
      return defineAsyncComponent({
        loader: () => import('@/components/FTUE/SetupProfile.vue'),
      });
    }

    return stepList[data.value.step].component;
  });

  const hasNextStep = computed(() => !!(stepList[data.value.step] && stepList[data.value.step].next));
  const hasPreviousStep = computed(() => !!(stepList[data.value.step] && stepList[data.value.step].previous));
  const stepTitle = computed(() => {
    if (stepList[data.value.step]) {
      return stepList[data.value.step].title;
    }
  });

  const nextStep = () => {
    if (hasNextStep.value) {
      data.value.step = stepList[data.value.step].next;
    }
  };

  const previousStep = () => {
    if (hasPreviousStep.value) {
      data.value.step = stepList[data.value.step].previous;
    }
  };

  return {
    data, ftueView, nextStep, previousStep, hasNextStep, hasPreviousStep, stepTitle,
  };
});
