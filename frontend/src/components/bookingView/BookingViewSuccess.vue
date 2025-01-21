<script setup lang="ts">
import { inject } from 'vue';
import { timeFormat } from '@/utils';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user-store';

import ArtSuccessfulBooking from '@/elements/arts/ArtSuccessfulBooking.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import { dayjsKey } from '@/keys';
import { Appointment, Slot } from '@/models';

const { t } = useI18n();
const router = useRouter();

const dj = inject(dayjsKey);
const user = useUserStore();

// component properties
interface Props {
  selectedEvent: Appointment & Slot,
  attendeeEmail: string,
  requested: boolean, // True if we are requesting a booking, false if already confirmed
}
defineProps<Props>();

</script>

<template>
  <div class="flex-center min-w-[50%] flex-col gap-12">
    <div class="text-2xl font-semibold text-teal-500">
      <span v-if="requested">{{ t('info.bookingSuccessfullyRequested') }}</span>
      <span v-else>{{ t('info.bookingSuccessfullyConfirmed') }}</span>
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
    <primary-button
      v-if="!user.authenticated"
      class="btn-start mt-12 p-7"
      :label="t('label.startUsingTba')"
      @click="router.push({ name: 'home' })"
    />
  </div>
  <art-successful-booking class="m-6 h-auto w-full max-w-md sm:w-auto sm:max-w-md"/>
</template>
