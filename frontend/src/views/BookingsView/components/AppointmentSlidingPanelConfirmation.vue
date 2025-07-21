<script setup lang="ts">
import { ref, inject, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { callKey } from '@/keys';
import { AvailabilitySlotResponse } from '@/models';
import ArtInvalidLink from '@/elements/arts/ArtInvalidLink.vue';
import ArtSuccessfulBooking from '@/elements/arts/ArtSuccessfulBooking.vue';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';
import { usePosthog, posthog } from '@/composables/posthog';
import { MetricEvents } from '@/definitions';

const { t } = useI18n();
const call = inject(callKey);

const props = defineProps<{
  signedUrl: string,
  slotId: number,
  slotToken: string;
  confirmed: boolean;
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>();

const isError = ref<boolean|null>(null);
const attendeeEmail = ref<string|null>(null);

onMounted(async () => {
  // build data object for put request
  const obj = {
    slot_id: props.slotId,
    slot_token: props.slotToken,
    owner_url: props.signedUrl,
    confirmed: props.confirmed,
  };
  const { error, data }: AvailabilitySlotResponse = await call('schedule/public/availability/booking').put(obj).json();
  if (error.value) {
    isError.value = true;
    return;
  }

  isError.value = false;
  attendeeEmail.value = data.value?.attendee?.email;

  if (usePosthog) {
    const event = props.confirmed ? MetricEvents.ConfirmBooking : MetricEvents.DenyBooking;
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
        {{ t('info.bookingLinkIsInvalid') }}
      </div>
      <div class="error-message">
        {{ t('text.invalidOrAlreadyBooked') }}
      </div>
    </div>
    <div v-else class="success-container">
      <art-successful-booking class="success-art" />
      <template v-if="confirmed">
        <div class="success-title">
          {{ t('info.bookingSuccessfullyConfirmed') }}
        </div>
        <div class="success-message">
          {{ t('info.eventWasCreated') }}<br>
          {{ t('text.invitationSentToAddress', { 'address': attendeeEmail }) }}
        </div>
      </template>
      <template v-else>
        <div class="success-title">
          {{ t('info.bookingSuccessfullyDenied') }}
        </div>
        <div class="success-message">
          {{ t('text.denialSentToAddress', { 'address': attendeeEmail }) }}<br>
          {{ t('info.slotIsAvailableAgain') }}
        </div>
      </template>
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

.error-message,
.success-message {
  color: var(--colour-ti-base);
  text-align: center;
}

:root.dark .error-message,
:root.dark .success-message {
  color: var(--colour-ti-secondary);
}
</style>
