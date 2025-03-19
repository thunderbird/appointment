import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useLocalStorage } from '@vueuse/core';
import { FtueStep } from '@/definitions';
import { Alert, Fetch, FtueState } from '@/models';

const initialObject = {
  // First step
  step: FtueStep.SetupProfile,
};

// eslint-disable-next-line import/prefer-default-export
export const useFTUEStore = defineStore('FTUE', () => {
  // State
  const data = useLocalStorage('tba/ftue', structuredClone(initialObject));
  const infoMessage = ref<Alert>(null);
  const errorMessage = ref<Alert>(null);
  const warningMessage = ref<Alert>(null);

  const call = ref(null);

  /**
   * Initialize store with data required at runtime
   *
   * @param fetch preconfigured function to perform API calls
   */
  const init = (fetch: Fetch) => {
    call.value = fetch;
  }

  /**
   * State information for navigating the First Time User Experience
   */
  const stepList: Record<FtueStep, FtueState> = {
    [FtueStep.SetupProfile]: {
      previous: null,
      next: FtueStep.CalendarProvider,
      title: 'ftue.steps.setupProfile',
    },
    [FtueStep.CalendarProvider]: {
      previous: FtueStep.SetupProfile,
      next: FtueStep.ConnectCalendars,
      title: 'ftue.steps.calendarProvider',
    },
    [FtueStep.ConnectCalendars]: {
      previous: FtueStep.CalendarProvider,
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

  const nextStep = async () => {
    if (hasNextStep.value) {
      clearMessages();
      data.value.step = stepList[data.value.step].next;

      if (call.value) {
        call.value('metrics/ftue-step').post({
          step_level: data.value.step,
          step_name: stepList[data.value.step].title.replace('ftue.steps.', ''),
        });
      }
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
    init,
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

export const createFTUEStore = (call: Fetch) => {
  const store = useFTUEStore();
  store.init(call);
  return store;
};
