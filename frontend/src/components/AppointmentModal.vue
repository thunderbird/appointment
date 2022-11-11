<template>
  <div v-if="open" class="bg-gray-800/50 w-screen h-screen fixed top-0 left-0 z-40" @click="emit('close')"></div>
  <div v-if="open" class="bg-white fixed z-50 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-xl p-12 max-w-3xl w-full">
    <div class="absolute top-8 right-8 cursor-pointer" @click="emit('close')">
      <icon-x class="h-6 w-6 stroke-1 stroke-gray-700 fill-transparent" />
    </div>
    <div class="text-xl mb-8">{{ appointment.title }}</div>
    <div class="grid grid-cols-4 text-gray-500 text-sm w-max gap-x-4 gap-y-2 pl-4 mb-8">
      <div class="font-semibold">{{ t('label.availabilityDay') }}</div>
      <div class="font-semibold">{{ t('label.startTime') }}</div>
      <div class="font-semibold">{{ t('label.endTime') }}</div>
      <div class="font-semibold">{{ t('label.bookings') }}</div>
      <template v-for="s in appointment.slots" :key="s.start">
        <div>{{ dj(s.start).format('LL') }}</div>
        <div>{{ dj(s.start).format('LT') }}</div>
        <div>{{ dj(s.start).add(s.duration, 'minutes').format('LT') }}</div>
        <div>{{ s.attendee?.email ?? '&mdash;' }}</div>
      </template>
    </div>
    <div class="grid grid-cols-3 text-gray-500 text-sm w-max gap-x-12 gap-y-8 pl-4">
      <div>
        <div class="font-semibold mb-1">{{ t('label.calendar') }}</div>
        <div>{{ appointment.calendar }}</div>
      </div>
      <div>
        <div class="font-semibold mb-1">{{ t('label.bookingLink') }}</div>
        <a :href="'https://apmt.day/' + appointment.slug" class="text-teal-500 underline" target="_blank">
          https://apmt.day/{{ appointment.slug }}
        </a>
      </div>
      <div></div>
      <div>
        <div class="font-semibold mb-1">{{ t('label.location') }}</div>
        <div>{{ appointment.location_name }}</div>
      </div>
      <div>
        <div class="font-semibold mb-1">{{ t('label.videoLink') }}</div>
        <a :href="appointment.location_url" class="text-teal-500 underline" target="_blank">
          {{ appointment.location_url }}
        </a>
      </div>
      <div>
        <div class="font-semibold mb-1">{{ t('label.activeAppointment') }}</div>
        <switch-toggle :active="appointment.mode === 'open'" />
      </div>
      <div class="col-span-3">
        <div class="font-semibold mb-1">{{ t('label.notes') }}</div>
        <div class="rounded-lg p-4 border border-gray-400">{{ appointment.details }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { inject } from 'vue';
import IconX from '@/elements/icons/IconX.vue';
import SwitchToggle from '@/elements/SwitchToggle.vue';
import { useI18n } from "vue-i18n";
const { t } = useI18n();
const dj = inject("dayjs");

// component properties
defineProps({
  open: Boolean, // modal state
  appointment: Object  // appointment data to display
});

// component emits
const emit = defineEmits(['close']);
</script>
