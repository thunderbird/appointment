import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { modalStates } from '@/definitions';

// eslint-disable-next-line import/prefer-default-export
export const useBookingModalStore = defineStore('bookingModal', () => {
  const open = ref(false);
  const state = ref(modalStates.open);
  const stateData = ref < string > (null);

  const isLoading = computed(() => state.value === modalStates.loading);
  const isFinished = computed(() => state.value === modalStates.finished);
  const hasErrors = computed(() => state.value === modalStates.error);
  const isEditable = computed(() => [modalStates.open, modalStates.error].indexOf(state.value) !== -1);

  /**
   * Restore default state, close modal and remove data
   */
  const $reset = () => {
    open.value = false;
    state.value = modalStates.open;
    stateData.value = null;
  };

  /**
   * Remove previous data and open modal
   */
  const openModal = () => {
    $reset();
    open.value = true;
  };

  /**
   * Remove previous data and close modal
   */
  const closeModal = () => {
    $reset();
    open.value = false;
  };

  return {
    open, state, stateData, hasErrors, isLoading, isFinished, isEditable, openModal, closeModal, $reset,
  };
});
