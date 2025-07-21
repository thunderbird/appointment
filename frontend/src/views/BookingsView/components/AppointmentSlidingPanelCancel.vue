<script setup lang="ts">
import { ref, inject, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { callKey } from '@/keys';
import { Appointment } from '@/models';
import ArtInvalidLink from '@/elements/arts/ArtInvalidLink.vue';
import ArtSuccessfulBooking from '@/elements/arts/ArtSuccessfulBooking.vue';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';
import { usePosthog, posthog } from '@/composables/posthog';
import { MetricEvents } from '@/definitions';

const { t } = useI18n();
const call = inject(callKey);

const props = defineProps<{
  cancelReason: string,
  appointment: Appointment | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>();

const isError = ref<boolean|null>(null);

onMounted(async () => {
  const { error } = await call(`apmt/${props.appointment?.id}/cancel`).post({
    reason: props.cancelReason
  }).json();

  if (error.value) {
    isError.value = true;
    return;
  }

  isError.value = false;

  if (usePosthog) {
    const event = MetricEvents.CancelBooking;
    posthog.capture(event);
  }

  // Close panel automatically after 7 seconds
  setTimeout(() => {
    emit('close');
  }, 7000);
});
</script>

<template>
  <div class="confirmation-container">
    <div v-if="isError === null" class="loading-container">
      <loading-spinner />
    </div>
    <div v-else-if="isError === true" class="error-container">
      <art-invalid-link class="error-art" />
      <div class="error-title">
        {{ t('info.bookingCancelError') }}
      </div>
    </div>
    <div v-else class="success-container">
      <art-successful-booking class="success-art" />
      <div class="success-title">
        {{ t('info.bookingSuccessfullyCancelled') }}
      </div>
    </div>
  </div>
</template>

<style>
.confirmation-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  flex-direction: column;
  gap: 3rem;
  padding: 0 1rem;
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
  text-align: center;
}
</style>
