<template>
  <div
    class="
      m-auto size-[95%] shrink-0 text-sm text-gray-700 hover:shadow-md dark:text-gray-200
      flex items-center gap-1.5 px-2 py-0.5
    "
    :class="{
      'rounded bg-amber-400/80 dark:text-white': event.all_day,
      'h-full rounded': !isMonthView,
    }"
    :style="{
      borderColor: eventColor(event, false).border,
      backgroundColor: isMonthView ? eventColor(event, false).background : event.calendar_color,
      color: !isMonthView ? getAccessibleColor(event.calendar_color) : null,
    }"
  >
    <div
      v-if="!event.all_day"
      class="mt-0.5 size-2.5 shrink-0 rounded-full"
      :class="{
        'bg-sky-400': !event.tentative,
        'border border-dashed border-sky-400/70': event.tentative,
      }"
      :style="{
        borderColor: event.tentative ? event.calendar_color : null,
        backgroundColor: !event.tentative ? event.calendar_color : null,
        color: !event.tentative ? getAccessibleColor(event.calendar_color) : null,
      }"
    ></div>
    <div class="grid">
      <div class="truncate rounded">
        {{ label }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { eventColor, getAccessibleColor } from '@/utils';

// component properties
const props = defineProps({
  isMonthView: Boolean, // flag, are we in month view?
  event: Object, // the event to show
  label: String, // event title
});
</script>
