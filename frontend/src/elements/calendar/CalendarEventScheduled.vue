<script setup lang="ts">
import { eventColor, getAccessibleColor } from '@/utils';
import { CustomEventData } from "@/models";

// component properties
interface Props {
  isMonthView: boolean; // flag, are we in month view?
  eventData: CustomEventData; // the event data to show
  label: string; // event title
};
defineProps<Props>();
</script>

<template>
  <div
    class="
      m-auto size-[95%] shrink-0 rounded border-2 border-dashed border-sky-400
      bg-sky-400/10 px-2 py-0.5 text-sm text-gray-700 hover:shadow-md dark:text-gray-200
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
