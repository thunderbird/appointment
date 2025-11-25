import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import { useRouter, useRoute } from 'vue-router';
import { useLocalStorage } from '@vueuse/core';
import { FtueStep } from '@/definitions';
import { Alert, Fetch } from '@/models';

const initialObject = {
  step: FtueStep.SetupProfile, // First step
};

export const useFTUEStore = defineStore('FTUE', () => {
  // State
  const data = useLocalStorage('tba/ftue', structuredClone(initialObject));
  const infoMessage = ref<Alert>(null);
  const errorMessage = ref<Alert>(null);
  const warningMessage = ref<Alert>(null);

  const call = ref(null);
  const router = useRouter();
  const route = useRoute();

  /**
   * Initialize store with data required at runtime
   *
   * @param fetch preconfigured function to perform API calls
   */
  const init = (fetch: Fetch) => {
    call.value = fetch;
  }

  const clearMessages = () => {
    infoMessage.value = null;
    errorMessage.value = null;
    warningMessage.value = null;
  };

  const moveToStep = async (newStep: FtueStep, replace = false) => {
    data.value.step = newStep;

    // Add query parameter to router history for browser back button support
    const routerMethod = replace ? router.replace : router.push;

    // First step (SetupProfile) doesn't have a query param
    const isFirstStep = newStep === FtueStep.SetupProfile;

    if (isFirstStep) {
      // Remove step query param for first step
      const restQuery = { ...route.query };
      delete restQuery.step;

      routerMethod({
        query: Object.keys(restQuery).length > 0 ? restQuery : undefined,
      });
    } else {
      routerMethod({
        query: {
          ...route.query,
          step: FtueStep[newStep],
        },
      });
    }

    if (call.value) {
      call.value('metrics/ftue-step').post({
        step_level: data.value.step,
        step_name: FtueStep[data.value.step],
      });
    }
  };

  /**
   * Sync step from query parameter without creating a new history entry
   * Used when navigating via browser back/forward buttons
   */
  const syncStepFromQuery = () => {
    const stepParam = route.query.step;

    if (stepParam && typeof stepParam === 'string') {
      const stepName = stepParam as keyof typeof FtueStep;
      const stepValue = FtueStep[stepName];

      if (stepValue !== undefined && stepValue !== data.value.step) {
        data.value.step = stepValue;
        clearMessages();
      }
    } else if (!stepParam) {
      // No query param means we're on the first step
      if (data.value.step !== FtueStep.SetupProfile) {
        data.value.step = FtueStep.SetupProfile;
        clearMessages();
      }
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
    currentStep,
    moveToStep,
    clearMessages,
    syncStepFromQuery,
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
