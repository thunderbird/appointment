<template>
  <div
    class="
      m-auto size-[95%] shrink-0 text-sm text-gray-700 hover:shadow-md dark:text-gray-200
      rounded border-2 border-dashed border-sky-400 bg-sky-400/10 px-2 py-0.5
    "
    :class="{ 'h-full': !isMonthView }"
    :style="{
      borderColor: eventColor(event, false).border,
      backgroundColor: isMonthView ? eventColor(event, false).background : event.calendar_color,
      color: !isMonthView ? getAccessibleColor(event.calendar_color) : null,
    }"
  >
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
