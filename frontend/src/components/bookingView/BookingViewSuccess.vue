<template>
  <div class="flex-center min-w-[50%] flex-col gap-12">
    <div class="text-2xl font-semibold text-teal-500">
      <span v-if="isAvailabilityRoute">{{ t('info.bookingSuccessfullyRequested') }}</span>
      <span v-else>{{ t('info.bookingSuccessful') }}</span>
    </div>
    <div class="flex w-full max-w-sm flex-col gap-1 rounded-lg shadow-lg">
      <div class="flex h-14 items-center justify-around rounded-t-md bg-teal-500">
        <div v-for="i in 2" :key="i" class="size-4 rounded-full bg-white"></div>
      </div>
      <div class="m-2 text-center text-2xl font-bold text-gray-500">
        {{ selectedEvent.title }}
      </div>
      <div class="m-2 flex flex-col gap-0.5 rounded-md bg-gray-100 py-2 text-center text-gray-500">
        <div class="text-sm font-semibold text-teal-500">{{ dj(selectedEvent.start).format('dddd') }}</div>
        <div class="text-lg">{{ dj(selectedEvent.start).format('LL') }}</div>
        <div class="flex-center gap-2 text-sm uppercase">
          <span>{{ dj(selectedEvent.start).format(timeFormat()) }}</span>
          <span>{{ dj.tz.guess() }}</span>
        </div>
      </div>
    </div>
    <div
      v-if="isBookingRoute"
      class="-mt-4 cursor-pointer text-sm text-teal-500 underline underline-offset-2"
      @click="emit('download')"
    >
      {{ t('label.downloadTheIcsFile') }}
    </div>
    <div v-if="isBookingRoute" class="text-center text-lg text-gray-700">
      <div>{{ t('info.invitationWasSent') }}</div>
      <div class="text-lg font-bold">
        {{ attendeeEmail }}
      </div>
    </div>
    <primary-button
      class="mt-12 p-7"
      :label="t('label.startUsingTba')"
      @click="router.push({ name: 'home' })"
    />
  </div>
  <art-successful-booking class="m-6 h-auto w-full max-w-md sm:w-auto sm:max-w-md"/>
</template>

<script setup>
import { inject } from 'vue';
import { timeFormat } from '@/utils';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

import ArtSuccessfulBooking from '@/elements/arts/ArtSuccessfulBooking';
import PrimaryButton from '@/elements/PrimaryButton';

const { t } = useI18n();
const router = useRouter();

const dj = inject('dayjs');

const emit = defineEmits(['download']);
defineProps({
  selectedEvent: Object,
  attendeeEmail: String,
  isAvailabilityRoute: Boolean,
  isBookingRoute: Boolean,
});

</script>
