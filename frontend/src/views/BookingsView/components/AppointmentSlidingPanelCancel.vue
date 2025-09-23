<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { Appointment } from '@/models';
import ArtInvalidLink from '@/elements/arts/ArtInvalidLink.vue';
import ArtSuccessfulBooking from '@/elements/arts/ArtSuccessfulBooking.vue';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';
import { PrimaryButton, DangerButton } from '@thunderbirdops/services-ui';
import { useAppointmentStore } from '@/stores/appointment-store';

const { t } = useI18n();
const appointmentStore = useAppointmentStore();

const props = defineProps<{
  appointment: Appointment | null
}>()

const emit = defineEmits<{
  (e: 'close'): void,
  (e: 'click:backButton'): void,
}>();

const confirmCancel = ref<boolean>(false);
const isError = ref<boolean|null>(null);

async function cancelAppointment() {
  confirmCancel.value = true;

  const { error } = await appointmentStore.cancelAppointment(props.appointment?.id);

  if (error.value) {
    isError.value = true;
    return;
  }

  isError.value = false;

  // Close panel automatically after 7 seconds
  setTimeout(() => {
    emit('close');
  }, 7000);
}
</script>

<template>
  <div class="confirmation-container">
    <template v-if="!confirmCancel">
      <div class="confirmation-header">
        <h2 class="confirmation-title">{{ t('label.areYouSure') }}</h2>
        <p class="confirmation-text">{{ t('info.bookingWillBeCanceled') }}</p>
      </div>
      <div class="confirmation-button-container">
        <primary-button
          variant="outline"
          data-testid="appointment-modal-confirm-cancel-back-btn"
          @click="emit('click:backButton')"
          :title="t('label.back')"
        >
          {{ t('label.back') }}
        </primary-button>
        <danger-button
          data-testid="appointment-modal-confirm-cancel-btn"
          @click="cancelAppointment()"
          :title="t('label.cancelBooking')"
        >
          {{ t('label.cancelBooking') }}
        </danger-button>
      </div>
    </template>

    <template v-else>
      <div v-if="isError === null" class="loading-container">
        <loading-spinner />
      </div>
      <div v-else-if="isError === true" class="error-container">
        <art-invalid-link class="error-art" />
        <div class="error-title">
          {{ t('error.bookingCancelError') }}
        </div>
      </div>
      <div v-else class="success-container">
        <art-successful-booking class="success-art" />
        <div class="success-title">
          {{ t('info.bookingSuccessfullyCancelled') }}
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.confirmation-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  flex-direction: column;
  gap: 3rem;
  padding: 0 1rem;
}

.confirmation-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  text-align: center;
}

.confirmation-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--colour-ti-critical);
}

.confirmation-text {
  font-size: 1.25rem;
  font-weight: 400;
  color: var(--colour-ti-base);
  text-align: center;
}

.confirmation-button-container {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;

  button {
    width: 100%;
  }

  @media (--sm) {
    button {
      width: auto;
    }
  }
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.error-container,
.success-container {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  gap: 2rem;
  padding: 0 1rem;
}

.error-art,
.success-art {
  margin: 1.5rem 0;
  height: auto;
  max-width: 24rem;
}

.error-title,
.success-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--colour-primary-default);
}
</style>
