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
  const infoMessage = ref(null);
  const errorMessage = ref(null);

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
      title: 'Create your profile',
    },
    [ftueStep.googlePermissions]: {
      previous: ftueStep.setupProfile,
      next: ftueStep.connectCalendars,
      title: 'Allow Google Calendar permissions',
    },
    [ftueStep.connectCalendars]: {
      previous: ftueStep.googlePermissions,
      next: ftueStep.setupSchedule,
      title: 'Connect calendars',
    },
    [ftueStep.setupSchedule]: {
      previous: ftueStep.connectCalendars,
      next: ftueStep.connectVideoConferencing,
      title: 'Set up your appointment availability',
    },
    [ftueStep.connectVideoConferencing]: {
      previous: ftueStep.setupSchedule,
      next: ftueStep.finish,
      title: 'Connect your video meeting link',
    },
    [ftueStep.finish]: {
      previous: ftueStep.connectVideoConferencing,
      next: 999,
      title: 'You are ready to start booking',
    },
  };

  /**
   * Returns a deferred component instance.
   * @type {ComputedRef}
   */
  const ftueView = computed(() => stepList[data.value.step]?.component ?? defineAsyncComponent({
    loader: () => import('@/components/FTUE/SetupProfile.vue'),
  }));

  const hasNextStep = computed(() => !!(stepList[data.value.step] && stepList[data.value.step].next));
  const hasPreviousStep = computed(() => !!(stepList[data.value.step] && stepList[data.value.step].previous));
  const stepTitle = computed(() => stepList[data.value.step]?.title ?? 'Unknown Step!');

  const clearMessages = () => {
    infoMessage.value = null;
    errorMessage.value = null;
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
    data, ftueView, nextStep, previousStep, currentStep, hasNextStep, hasPreviousStep, stepTitle, $reset, infoMessage, errorMessage,
  };
});
