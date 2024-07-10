<script setup lang="ts">
import { eventColor, getAccessibleColor } from '@/utils';

// component properties
defineProps({
  isMonthView: Boolean, // flag, are we in month view?
  event: Object, // the event to show
  label: String, // event title
});
</script>

<template>
  <div
    class="
      m-auto flex size-[95%] shrink-0 items-center rounded border-l-4
      border-teal-400 px-2 text-sm text-gray-700 hover:shadow-md dark:text-gray-200
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
