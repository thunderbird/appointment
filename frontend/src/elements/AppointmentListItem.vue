<template>
  <div class="flex gap-2 items-stretch">
    <div class="w-1.5 rounded-lg" :style="{ 'background-color': appointment.calendar_color }"></div>
    <div class="w-full">
      <div class="flex justify-between">
        <div>
          <div>{{ appointment.title }}</div>
          <div class="text-sm">
            {{ hDuration(appointment.duration) }},
            {{ t('label.' + keyByValue(locationTypes, appointment.location_type)) }}
          </div>
        </div>
        <icon-dots-vertical class="h-6 w-6 stroke-slate-400 stroke-2 fill-slate-400" />
      </div>
      <div class="flex justify-between items-center">
        <router-link
          :to="{ name: 'booking', params: { 'slug': appointment.slug } }"
          class="text-sm text-teal-500 underline"
        >
          {{ t('label.viewBooking') }}
        </router-link>
        <text-button :label="t('label.copyLink')" :copy="baseurl + appointment.slug" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { inject } from 'vue';
import { keyByValue } from '@/utils';
import { locationTypes } from '@/definitions';
import { useI18n } from 'vue-i18n';
import IconDotsVertical from '@/elements/icons/IconDotsVertical';
import TextButton from '@/elements/TextButton';

const baseurl = inject('baseurl');
const hDuration = inject('hDuration');
const { t } = useI18n();

// component properties
defineProps({
  appointment: Object, // appointment to show details for
});
</script>
