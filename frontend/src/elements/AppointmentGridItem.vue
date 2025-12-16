<script setup lang="ts">
import { BookingStatus } from '@/definitions';
import { inject, computed } from 'vue';
import { keyByValue, timeFormat } from '@/utils';
import { useI18n } from 'vue-i18n';
import { Appointment } from '@/models';

// icons
import {
  PhLightbulb,
  PhCalendarBlank,
  PhClock,
} from '@phosphor-icons/vue';
import { dayjsKey, paintBackgroundKey } from '@/keys';

// component constants
const { t } = useI18n();
const paintBackground = inject(paintBackgroundKey);
const dj = inject(dayjsKey);

// component properties
interface Props {
  appointment: Appointment; // appointment to show details for
}
const props = defineProps<Props>();

// true if an appointment from the past was given
const isPast = computed(() => props.appointment.slots[0].start < dj());

// true if a pending appointment was given
const isPending = computed(() => props.appointment.slots[0].booking_status === BookingStatus.Requested);
</script>

<template>
  <div
    class="rounded border-l-8 border-sky-400"
    :class="{
      'bg-gray-300 text-gray-500 opacity-50 dark:bg-gray-600 dark:text-gray-400': isPast,
      'cursor-pointer hover:bg-sky-400/10 hover:shadow-md': !isPast,
    }"
    :style="{ borderColor: appointment.calendar_color }"
    @mouseover="el => !isPast ? paintBackground(el, appointment.calendar_color, '22') : null"
    @mouseout="el => !isPast ? paintBackground(el, appointment.calendar_color, undefined, true) : null"
  >
    <div
      class="flex h-full flex-col gap-1 rounded-r border-y-2 border-r-2 border-solid border-sky-400 px-4 py-3"
      :class="{ 'border-dashed': isPending }"
      :style="{ borderColor: appointment.calendar_color }"
    >
      <div>{{ appointment.title }}</div>
      <div class="flex items-center gap-1 text-sm">
        <ph-lightbulb class="size-4 shrink-0 fill-transparent stroke-gray-500 stroke-2"/>
        {{ t('label.' + keyByValue(BookingStatus, appointment?.slots[0].booking_status ?? 'Unknown', true)) }}
      </div>
      <div class="flex items-center gap-1 text-sm">
        <ph-calendar-blank class="size-4 shrink-0 fill-transparent stroke-gray-500 stroke-2"/>
        {{ appointment.calendar_title }}
      </div>
      <div class="flex items-center gap-1 text-sm">
        <ph-clock class="size-4 shrink-0 fill-transparent stroke-gray-500 stroke-2"/>
        <div>{{ dj(appointment?.slots[0].start).format('LL') }}</div>
        <div>{{ dj(appointment?.slots[0].start).format(timeFormat()) }}</div>
        <div>{{ t('label.to') }}</div>
        <div>{{ dj(appointment?.slots[0].start).add(appointment?.slots[0].duration, 'minutes').format(timeFormat()) }}</div>
      </div>
    </div>
  </div>
</template>
