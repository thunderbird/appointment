import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { ModalStates } from '@/definitions';

 
export const useBookingModalStore = defineStore('bookingModal', () => {
  const open = ref(false);
  const state = ref(ModalStates.Open);
  const stateData = ref<string>(null);

  const isLoading = computed(() => state.value === ModalStates.Loading);
  const isFinished = computed(() => state.value === ModalStates.Finished);
  const hasErrors = computed(() => state.value === ModalStates.Error);
  const isEditable = computed(() => [ModalStates.Open, ModalStates.Error].indexOf(state.value) !== -1);

  /**
   * Restore default state, close modal and remove data
   */
  const $reset = () => {
    open.value = false;
    state.value = ModalStates.Open;
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
