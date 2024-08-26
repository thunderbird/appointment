import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useLocalStorage } from '@vueuse/core';
import { FtueStep } from '@/definitions';
import { Fetch } from '@/models';

const initialObject = {
  // First step
  step: FtueStep.SetupProfile,
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
   *   previous: null|FtueStep,
   *   next: null|FtueStep,
   *   title: string,
   * }}
   */
  const stepList = {
    [FtueStep.SetupProfile]: {
      previous: null,
      next: FtueStep.GooglePermissions,
      title: 'ftue.steps.setupProfile',
    },
    [FtueStep.GooglePermissions]: {
      previous: FtueStep.SetupProfile,
      next: FtueStep.ConnectCalendars,
      title: 'ftue.steps.googlePermissions',
    },
    [FtueStep.ConnectCalendars]: {
      previous: FtueStep.GooglePermissions,
      next: FtueStep.SetupSchedule,
      title: 'ftue.steps.connectCalendars',
    },
    [FtueStep.SetupSchedule]: {
      previous: FtueStep.ConnectCalendars,
      next: FtueStep.ConnectVideoConferencing,
      title: 'ftue.steps.setupSchedule',
    },
    [FtueStep.ConnectVideoConferencing]: {
      previous: FtueStep.SetupSchedule,
      next: FtueStep.Finish,
      title: 'ftue.steps.connectVideo',
    },
    [FtueStep.Finish]: {
      previous: FtueStep.ConnectVideoConferencing,
      next: FtueStep.Finish,
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

  const nextStep = async (call: Fetch) => {
    if (hasNextStep.value) {
      clearMessages();
      data.value.step = stepList[data.value.step].next;

      call('metrics/ftue-step').post({
        step_level: data.value.step,
        step_name: stepList[data.value.step].title.replace('ftue.steps.', ''),
      });
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
    data.value.step = FtueStep.SetupProfile;
    clearMessages();
  };

  return {
    data,
    nextStep,
    previousStep,
    currentStep,
    hasNextStep,
    hasPreviousStep,
    stepTitle,
    $reset,
    infoMessage,
    errorMessage,
    warningMessage,
  };
});
