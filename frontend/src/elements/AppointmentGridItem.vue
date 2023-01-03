<template>
  <div
    class="w-1/4 hover:bg-sky-400/10 hover:shadow-md rounded border-dashed border-t-2 border-r-2 border-b-2 border-sky-400 cursor-pointer"
    :style="{ 'border-color': appointment.calendar_color }"
    @mouseover="el => el.currentTarget.style.backgroundColor=appointment.calendar_color + '22'"
    @mouseout="el => el.currentTarget.style.backgroundColor='transparent'"
  >
    <div
      class="h-full px-4 py-3 rounded border-l-8 border-sky-400"
      :style="{ 'border-color': appointment.calendar_color }"
    >
      <div>{{ appointment.title }}</div>
      <div class="pl-4 text-sm">{{ t('label.' + keyByValue(appointmentState, appointment.status)) }}</div>
      <div class="pl-4 text-sm">{{ appointment.calendar_title }}</div>
      <div class="px-4 text-sm">
        <switch-toggle :active="appointment.active" :label="t('label.activeAppointment')" @click.stop="null" />
      </div>
      <div class="pl-4 text-sm whitespace-nowrap overflow-hidden overflow-ellipsis">
        <a :href="baseurl + appointment.slug" class="text-teal-500 underline" target="_blank" @click.stop="null">
          {{ baseurl + appointment.slug }}
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { appointmentState } from '@/definitions';
import { inject } from 'vue';
import { keyByValue } from '@/utils';
import { useI18n } from 'vue-i18n';
import SwitchToggle from '@/elements/SwitchToggle';

const baseurl = inject('baseurl');
const { t } = useI18n();

// component properties
defineProps({
  appointment: Object, // appointment to show details for
});
</script>
