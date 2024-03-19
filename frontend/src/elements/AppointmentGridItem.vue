<template>
  <div
    class="rounded border-l-8 border-sky-400"
    :class="{
      'bg-gray-300 text-gray-500 opacity-50 dark:bg-gray-600 dark:text-gray-400': isPast,
      'cursor-pointer hover:bg-sky-400/10 hover:shadow-md': !isPast,
    }"
    :style="{ borderColor: appointment.calendar_color }"
    @mouseover="el => !isPast ? paintBackground(el, appointment.calendar_color, '22') : null"
    @mouseout="el => !isPast ? paintBackground(el, appointment.calendar_color, _, true) : null"
  >
    <div
      class="flex h-full flex-col gap-1 rounded-r border-y-2 border-r-2 border-solid border-sky-400 px-4 py-3"
      :class="{ 'border-dashed': isPending }"
      :style="{ borderColor: appointment.calendar_color }"
    >
      <div>{{ appointment.title }}</div>
      <div class="flex items-center gap-1 text-sm">
        <icon-bulb class="size-4 shrink-0 fill-transparent stroke-gray-500 stroke-2"/>
        {{ t('label.' + keyByValue(bookingStatus, appointment?.slots[0].booking_status ?? 'Unknown')) }}
      </div>
      <div class="flex items-center gap-1 text-sm">
        <icon-calendar class="size-4 shrink-0 fill-transparent stroke-gray-500 stroke-2"/>
        {{ appointment.calendar_title }}
      </div>
      <div class="flex items-center gap-1 text-sm">
        <icon-clock class="size-4 shrink-0 fill-transparent stroke-gray-500 stroke-2"/>
        <div>{{ dj(appointment?.slots[0].start).format('LL') }}</div>
        <div>{{ dj(appointment?.slots[0].start).format(timeFormat()) }}</div>
        <div>{{ t('label.to') }}</div>
        <div>{{ dj(appointment?.slots[0].start).add(appointment?.slots[0].duration, 'minutes').format(timeFormat()) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { appointmentState, bookingStatus } from '@/definitions';
import { inject, computed } from 'vue';
import { keyByValue, timeFormat } from '@/utils';
import { useI18n } from 'vue-i18n';

// icons
import {
  IconBulb,
  IconCalendar,
  IconClock,
  IconLink,
} from '@tabler/icons-vue';

// component constants
const { t } = useI18n();
const bookingUrl = inject('bookingUrl');
const paintBackground = inject('paintBackground');
const dj = inject('dayjs');

// component properties
const props = defineProps({
  appointment: Object, // appointment to show details for
});

// true if an appointment from the past was given
const isPast = computed(() => props.appointment.status === appointmentState.past);

// true if a pending appointment was given
const isPending = computed(() => props.appointment.status === appointmentState.pending);
</script>
