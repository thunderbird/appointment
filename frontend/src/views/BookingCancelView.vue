<script setup lang="ts">
import { inject, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { callKey, dayjsKey } from '@/keys';
import { Appointment, Attendee, Slot } from '@/models';
import { BookingResultState, BookingStatus } from '@/definitions';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';
import BookingViewResult from '@/views/BookerView/components/BookingViewResult.vue';
import BookingViewError from '@/views/BookerView/components/BookingViewError.vue';

const { t } = useI18n();
const route = useRoute();
const call = inject(callKey);
const dj = inject(dayjsKey);

// retrieve all required data from url
const slotId = Number(route.params.slot);
const slotToken = route.params.token as string;

const isLoading = ref(true);
const isError = ref(false);
const selectedEvent = ref<Appointment & Slot>(null);
const attendee = ref<Attendee>(null);
const state = ref<BookingResultState>(null);

// Load the booking details, only open and upcoming bookings with a valid token are returned
onMounted(async () => {
  const { data, error } = await call('schedule/public/availability/cancel/details')
    .post({ slot_id: slotId, slot_token: slotToken })
    .json();

  isLoading.value = false;

  if (error.value) {
    isError.value = true;
    return;
  }

  const { slot } = data.value;
  selectedEvent.value = {
    ...slot,
    start: dj.utc(slot.start).tz(dj.tz.guess()),
    booking_tkn: slotToken,
  };
  attendee.value = data.value.attendee;
  state.value =
    slot.booking_status === BookingStatus.Requested ? BookingResultState.Requested : BookingResultState.Confirmed;
});
</script>

<template>
  <main v-if="isLoading" class="booking-loading-container">
    <loading-spinner />
  </main>
  <main v-else-if="isError" class="booking-invalid-container">
    <booking-view-error :heading="t('info.bookingCancelLinkIsInvalid')" :body="t('text.bookingCannotBeCancelled')" />
  </main>
  <main v-else class="booking-success-container">
    <booking-view-result :selected-event="selectedEvent" :attendee="attendee" :state="state" />
  </main>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.booking-loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.booking-invalid-container {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  gap: 2rem;
  padding: 0 1rem;
}

.booking-success-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0 1rem;
  gap: 2rem;
}

@media (--md) {
  .booking-success-container {
    flex-direction: row;
    align-items: start;
  }
}
</style>
