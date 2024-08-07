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
  <div class="flex-center h-full flex-col gap-12 p-4">
    <div v-if="isError === null">
      <loading-spinner />
    </div>
    <div v-else-if="isError === true" class="flex-center flex-col gap-8 px-4">
      <art-invalid-link class="my-6 h-auto max-w-sm" />
      <div class="text-xl font-semibold text-sky-600">
        {{ t('info.bookingLinkIsInvalid') }}
      </div>
      <div class="text-gray-800 dark:text-gray-300">
        {{ t('text.invalidOrAlreadyBooked') }}
      </div>
    </div>
    <div v-else class="flex-center flex-col gap-8 px-4">
      <art-successful-booking class="my-6 h-auto max-w-sm" />
      <template v-if="confirmed">
        <div class="text-xl font-semibold text-sky-600">
          {{ t('info.bookingSuccessfullyConfirmed') }}
        </div>
        <div class="text-center text-gray-800 dark:text-gray-300">
          {{ t('info.eventWasCreated') }}<br>
          {{ t('text.invitationSentToAddress', { 'address': attendeeEmail }) }}
        </div>
      </template>
      <template v-else>
        <div class="text-xl font-semibold text-sky-600">
          {{ t('info.bookingSuccessfullyDenied') }}
        </div>
        <div class="text-center text-gray-800 dark:text-gray-300">
          {{ t('text.denialSentToAddress', { 'address': attendeeEmail }) }}<br>
          {{ t('info.slotIsAvailableAgain') }}
        </div>
      </template>
    </div>
  </div>

</template>
