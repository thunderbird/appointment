<template>
  <div class="flex-center flex-col gap-12 min-w-[50%]">
    <div class="text-2xl font-semibold text-teal-500">
      <span v-if="isAvailabilityRoute">{{ t('info.bookingSuccessfullyRequested') }}</span>
      <span v-else>{{ t('info.bookingSuccessful') }}</span>
    </div>
    <div class="w-full max-w-sm shadow-lg rounded-lg flex flex-col gap-1">
      <div class="rounded-t-md bg-teal-500 h-14 flex justify-around items-center">
        <div v-for="i in 2" :key="i" class="rounded-full bg-white w-4 h-4"></div>
      </div>
      <div class="text-2xl font-bold m-2 text-center text-gray-500">
        {{ selectedEvent.title }}
      </div>
      <div class="flex flex-col gap-0.5 m-2 py-2 rounded-md text-center bg-gray-100 text-gray-500">
        <div class="text-teal-500 font-semibold text-sm">{{ dj(selectedEvent.start).format('dddd') }}</div>
        <div class="text-lg">{{ dj(selectedEvent.start).format('LL') }}</div>
        <div class="text-sm uppercase flex-center gap-2">
          <span>{{ dj(selectedEvent.start).format(timeFormat()) }}</span>
          <span>{{ dj.tz.guess() }}</span>
        </div>
      </div>
    </div>
    <div
      v-if="isBookingRoute"
      class="text-teal-500 text-sm underline underline-offset-2 -mt-4 cursor-pointer"
      @click="emit('download')"
    >
      {{ t('label.downloadTheIcsFile') }}
    </div>
    <div v-if="isBookingRoute" class="text-gray-700 text-lg text-center">
      <div>{{ t('info.invitationWasSent') }}</div>
      <div class="font-bold text-lg">
        {{ attendeeEmail }}
      </div>
    </div>
    <primary-button
      class="p-7 mt-12"
      :label="t('label.startUsingTba')"
      @click="router.push({ name: 'home' })"
    />
  </div>
  <art-successful-booking class="max-w-md w-full sm:max-w-md sm:w-auto h-auto m-6"/>
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
