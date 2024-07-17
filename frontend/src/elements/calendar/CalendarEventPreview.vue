<script setup lang="ts">
import { eventColor, getAccessibleColor } from '@/utils';
import { CustomEventData } from "@/models";

// component properties
interface Props {
  isMonthView: boolean, // flag, are we in month view?
  eventData: CustomEventData, // the event data to show
  label: string, // event title
};
defineProps<Props>();

</script>

<template>
  <div
    class="
      m-auto flex size-[95%] shrink-0 items-center rounded border-l-4
      border-teal-400 px-2 text-sm text-gray-700 hover:shadow-md dark:text-gray-200
    "
    :class="{ 'h-full': !isMonthView }"
    :style="{
      borderColor: eventColor(eventData, false).border,
      backgroundColor: isMonthView ? eventColor(eventData, false).background : eventData.calendar_color,
      color: !isMonthView ? getAccessibleColor(eventData.calendar_color) : null,
    }"
  >
    <div class="grid">
      <div class="truncate rounded">
        {{ label }}
      </div>
    </div>
  </div>
</template>
