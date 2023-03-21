<template>
  <div class="flex gap-2 items-stretch">
    <div class="w-1.5 rounded-lg shrink-0" :style="{ 'background-color': appointment.calendar_color }"></div>
    <div class="w-[95%]">
      <div class="flex justify-between">
        <div class="overflow-x-hidden">
          <div class="truncate">{{ appointment.title }}</div>
          <div class="text-sm">
            <span v-if="appointment.duration">{{ hDuration(appointment.duration) }},</span>
            {{ t('label.' + keyByValue(locationTypes, appointment.location_type)) }}
          </div>
        </div>
        <icon-dots-vertical class="h-6 w-6 shrink-0 stroke-gray-400 stroke-2 fill-gray-400" />
      </div>
      <div class="flex justify-between items-center">
        <router-link
          :to="{ name: 'booking', params: { 'slug': appointment.slug } }"
          class="text-sm shrink text-teal-500 underline underline-offset-2"
        >
          {{ t('label.viewBooking') }}
        </router-link>
        <text-button :label="t('label.copyLink')" :copy="bookingUrl + appointment.slug" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { inject } from 'vue';
import { keyByValue } from '@/utils';
import { locationTypes } from '@/definitions';
import { useI18n } from 'vue-i18n';
import TextButton from '@/elements/TextButton';

// icons
import { IconDotsVertical } from '@tabler/icons-vue';

// component constants
const bookingUrl = inject('bookingUrl');
const hDuration = inject('hDuration');
const { t } = useI18n();

// component properties
defineProps({
  appointment: Object, // appointment to show details for
});
</script>
