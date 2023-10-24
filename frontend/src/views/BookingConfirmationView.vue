<template>
  <div class="h-full p-4 flex-center flex-col gap-12">
    <div v-if="isError === null">
      <loading-spinner />
    </div>
    <div v-else-if="isError === true" class="px-4 flex-center flex-col gap-8">
      <art-invalid-link class="max-w-sm h-auto my-6" />
      <div class="text-xl font-semibold text-sky-600">
        {{ t('info.bookingLinkIsInvalid') }}
      </div>
      <div class="text-gray-800 dark:text-gray-300">
        {{ t('text.invalidOrAlreadyBooked') }}
      </div>
    </div>
    <div v-else class="px-4 flex-center flex-col gap-8">
      <art-successful-booking class="max-w-sm h-auto my-6" />
      <template v-if="confirmed">
        <div class="text-xl font-semibold text-sky-600">
          {{ t('info.bookingSuccessfullyConfirmed') }}
        </div>
        <div class="text-gray-800 dark:text-gray-300">
          {{ t('info.eventWasCreated') }}
          {{ t('text.invitationSentToAddress') }}
        </div>
      </template>
      <template v-else="confirmed">
        <div class="text-xl font-semibold text-sky-600">
          {{ t('info.bookingSuccessfullyDenied') }}
        </div>
        <div class="text-gray-800 dark:text-gray-300">
          {{ t('text.denialSentToAddress') }}
          {{ t('info.slotIsAvailableAgain') }}
        </div>
      </template>
    </div>
  </div>

</template>

<script setup>
// import { useAuth0 } from '@auth0/auth0-vue';
import { ref, inject, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from "vue-router";
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
const confirmed = Boolean(route.params.confirmed);

// const auth = useAuth0();
// const isAuthenticated = computed(() => auth.isAuthenticated.value);
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
    confirmed: confirmed,
  };
  const { error, data } = await call('schedule/public/availability/booking').put(obj).json();
  if (error.value) {
    isError.value = true;
  } else {
    isError.value = false;
    event.value = data.value.slot;
    attendee.value = data.value.attendee;
  }
});
</script>
