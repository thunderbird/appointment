<script setup lang="ts">
import { ref, inject, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { callKey } from '@/keys';
import { AvailabilitySlotResponse } from '@/models';
import ArtInvalidLink from '@/elements/arts/ArtInvalidLink.vue';
import ArtSuccessfulBooking from '@/elements/arts/ArtSuccessfulBooking.vue';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';
import { usePosthog, posthog } from '@/composables/posthog';
import { MetricEvents } from '@/definitions';

const { t } = useI18n();
const route = useRoute();
const call = inject(callKey);

// retrieve all required data from url
const [signedUrl] = window.location.href.split('/confirm/');
const slotId = Number(route.params.slot);
const slotToken = route.params.token;
const confirmed = parseInt(route.params.confirmed as string) === 1;

const isError = ref<boolean|null>(null);
const attendeeEmail = ref<string|null>(null);

// initially load data when component gets remounted
onMounted(async () => {
  // build data object for put request
  const obj = {
    slot_id: slotId,
    slot_token: slotToken,
    owner_url: signedUrl,
    confirmed,
  };
  const { error, data }: AvailabilitySlotResponse = await call('schedule/public/availability/booking').put(obj).json();
  if (error.value) {
    isError.value = true;

    return;
  }

  isError.value = false;
  attendeeEmail.value = data.value?.attendee?.email;

  if (usePosthog) {
    const event = confirmed ? MetricEvents.ConfirmBooking : MetricEvents.DenyBooking;
    posthog.capture(event);
  }
});
</script>

<template>
  <div class="booking-confirmation-view-container">
    <div v-if="isError === null">
      <loading-spinner />
    </div>
    <div v-else-if="isError === true" class="content">
      <art-invalid-link class="art" />
      <h1>{{ t('info.bookingLinkIsInvalid') }}</h1>
      <p>{{ t('text.invalidOrAlreadyBooked') }}</p>
    </div>
    <div v-else class="content">
      <art-successful-booking class="art" />
      <template v-if="confirmed">
        <h1>{{ t('info.bookingSuccessfullyConfirmed') }}</h1>
        <p>
          {{ t('info.eventWasCreated') }}<br>
          {{ t('text.invitationSentToAddress', { 'address': attendeeEmail }) }}
        </p>
      </template>
      <template v-else>
        <h1>{{ t('info.bookingSuccessfullyDenied') }}</h1>
        <p>
          {{ t('text.denialSentToAddress', { 'address': attendeeEmail }) }}<br>
          {{ t('info.slotIsAvailableAgain') }}
        </p>
      </template>
    </div>
  </div>
</template>

<style scoped>
.booking-confirmation-view-container {
  display: flex;
  flex-direction: column;
  gap: 3rem;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 1rem;

  .content {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    align-items: center;
    justify-content: center;
    padding-inline: 1rem;

    h1 {
      font-size: 1.25rem;
      line-height: 1.75rem;
      font-weight: 600;
      color: var(--colour-ti-highlight);
    }

    p {
      text-align: center;
      color: var(--colour-ti-secondary);
    }

    .art {
      margin-block: 1.5rem;
      height: auto;
      max-width: 24rem;
    }
  }
}
</style>