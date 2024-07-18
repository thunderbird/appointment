import { defineStore } from 'pinia';
import { ref, computed, defineAsyncComponent } from 'vue';
import { useLocalStorage } from '@vueuse/core';
import { ftueStep } from '@/definitions';

const initialObject = {
  // First step
  step: ftueStep.setupProfile,
};

// eslint-disable-next-line import/prefer-default-export
export const useFTUEStore = defineStore('FTUE', () => {
  // State
  const data = useLocalStorage('tba/ftue', structuredClone(initialObject));
  const infoMessage = ref(null);
  const errorMessage = ref(null);
  const warningMessage = ref(null);

  /**
   * State information for navigating the First Time User Experience
   * @type {{
   *   previous: null|ftueStep,
   *   next: null|ftueStep,
   *   title: string,
   *   component: ComponentPublicInstance,
   * }}
   */
  const stepList = {
    [ftueStep.setupProfile]: {
      previous: null,
      next: ftueStep.googlePermissions,
      title: 'ftue.steps.setupProfile',
    },
    [ftueStep.googlePermissions]: {
      previous: ftueStep.setupProfile,
      next: ftueStep.connectCalendars,
      title: 'ftue.steps.googlePermissions',
    },
    [ftueStep.connectCalendars]: {
      previous: ftueStep.googlePermissions,
      next: ftueStep.setupSchedule,
      title: 'ftue.steps.connectCalendars',
    },
    [ftueStep.setupSchedule]: {
      previous: ftueStep.connectCalendars,
      next: ftueStep.connectVideoConferencing,
      title: 'ftue.steps.setupSchedule',
    },
    [ftueStep.connectVideoConferencing]: {
      previous: ftueStep.setupSchedule,
      next: ftueStep.finish,
      title: 'ftue.steps.connectVideo',
    },
    [ftueStep.finish]: {
      previous: ftueStep.connectVideoConferencing,
      next: ftueStep.finish,
      title: 'ftue.steps.finish',
    },
  };

  const hasNextStep = computed(() => !!(stepList[data.value.step] && stepList[data.value.step].next));
  const hasPreviousStep = computed(() => !!(stepList[data.value.step] && stepList[data.value.step].previous));
  const stepTitle = computed(() => stepList[data.value.step]?.title ?? 'ftue.steps.error');

  const clearMessages = () => {
    infoMessage.value = null;
    errorMessage.value = null;
    warningMessage.value = null;
  };

  const nextStep = async () => {
    if (hasNextStep.value) {
      clearMessages();
      data.value.step = stepList[data.value.step].next;
    }
  };

  const previousStep = () => {
    if (hasPreviousStep.value) {
      clearMessages();
      data.value.step = stepList[data.value.step].previous;
    }
  };

  const currentStep = computed(() => data.value.step);
  const $reset = () => {
    data.value.step = ftueStep.setupProfile;
    clearMessages();
  };

  return {
    data, nextStep, previousStep, currentStep, hasNextStep, hasPreviousStep, stepTitle, $reset, infoMessage, errorMessage, warningMessage,
  };
});
