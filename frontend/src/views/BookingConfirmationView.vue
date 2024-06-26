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
          {{ t('text.invitationSentToAddress', { 'address': attendee?.email }) }}
        </div>
      </template>
      <template v-else>
        <div class="text-xl font-semibold text-sky-600">
          {{ t('info.bookingSuccessfullyDenied') }}
        </div>
        <div class="text-center text-gray-800 dark:text-gray-300">
          {{ t('text.denialSentToAddress', { 'address': attendee?.email }) }}<br>
          {{ t('info.slotIsAvailableAgain') }}
        </div>
      </template>
    </div>
  </div>

</template>

<script setup>
import { ref, inject, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import ArtInvalidLink from '@/elements/arts/ArtInvalidLink';
import ArtSuccessfulBooking from '@/elements/arts/ArtSuccessfulBooking';
import LoadingSpinner from '@/elements/LoadingSpinner';

const { t } = useI18n();
const route = useRoute();
const call = inject('call');

// retrieve all required data from url
const [signedUrl] = window.location.href.split('/confirm/');
const slotId = Number(route.params.slot);
const slotToken = route.params.token;
const confirmed = parseInt(route.params.confirmed) === 1;

const isError = ref(null);
const event = ref(null);
const attendee = ref(null);

// initially load data when component gets remounted
onMounted(async () => {
  // build data object for put request
  const obj = {
    slot_id: slotId,
    slot_token: slotToken,
    owner_url: signedUrl,
    confirmed,
  };
  const { error, data } = await call('schedule/public/availability/booking').put(obj).json();
  if (error.value) {
    isError.value = true;
  } else {
    isError.value = false;
    event.value = data.value?.slot;
    attendee.value = data.value?.attendee;
  }
});
</script>
