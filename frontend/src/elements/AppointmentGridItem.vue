<template>
  <div
    class="rounded border-l-8 border-sky-400"
    :class="{
      'opacity-50 bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400': appointment.status === appointmentState.past,
      'cursor-pointer hover:shadow-md hover:bg-sky-400/10': appointment.status !== appointmentState.past,
    }"
    :style="{ 'border-color': appointment.calendar_color }"
    @mouseover="el => appointment.status !== appointmentState.past ? paintBackground(el, appointment.calendar_color, '22') : null"
    @mouseout="el => appointment.status !== appointmentState.past ? paintBackground(el, appointment.calendar_color, _, true) : null"
  >
    <div
      class="h-full px-4 py-3 rounded-r border-solid border-t-2 border-r-2 border-b-2 border-sky-400 flex flex-col gap-1"
      :class="{ 'border-dashed': appointment.status == appointmentState.pending }"
      :style="{ 'border-color': appointment.calendar_color }"
    >
      <div>{{ appointment.title }}</div>
      <div class="text-sm flex items-center gap-1">
        <icon-clock class="h-4 w-4 stroke-gray-500 stroke-2 fill-transparent shrink-0" />
        {{ t('label.' + keyByValue(appointmentState, appointment.status)) }}
      </div>
      <div class="text-sm flex items-center gap-1">
        <icon-calendar class="h-4 w-4 stroke-gray-500 stroke-2 fill-transparent shrink-0" />
        {{ appointment.calendar_title }}
      </div>
      <div class="pr-4 text-sm flex items-center gap-1">
        <icon-bulb class="h-4 w-4 stroke-gray-500 stroke-2 fill-transparent shrink-0" />
        <switch-toggle
          :label="t('label.activeAppointment')"
          :active="appointment.active"
          :disabled="true"
          @click.stop="null"
        />
      </div>
      <div class="text-sm flex items-center gap-1">
        <icon-link class="h-4 w-4 stroke-gray-500 stroke-2 fill-transparent shrink-0" />
        <div class="truncate">
          <a :href="baseurl + appointment.slug" class="text-teal-500 underline underline-offset-2" target="_blank" @click.stop="null">
            {{ baseurl + appointment.slug }}
          </a>
        </div>
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

// icons
import {
  IconBulb,
  IconCalendar,
  IconClock,
  IconLink,
} from '@tabler/icons-vue';

// component constants
const { t } = useI18n();
const baseurl = inject('baseurl');
const paintBackground = inject('paintBackground');

// component properties
defineProps({
  appointment: Object, // appointment to show details for
});
</script>
