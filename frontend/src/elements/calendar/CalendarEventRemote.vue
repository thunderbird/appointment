<script setup lang="ts">
import { eventColor, getAccessibleColor } from '@/utils';
import { computed } from 'vue';
import { CustomEventData } from "@/models";

// component properties
interface Props {
  isMonthView: boolean, // flag, are we in month view?
  eventData: CustomEventData, // the event data to show
  label: string, // event title
};
const props = defineProps<Props>();

const eventBackgroundColor = computed(() => {
  if (props.eventData.all_day) {
    return null;
  }
  if (props.isMonthView || (!props.isMonthView && props.eventData.tentative)) {
    return 'transparent';
  }
  return props.eventData.calendar_color;
});

const eventTextColor = computed(() => {
  if (props.isMonthView) {
    return null;
  }
  if (props.eventData.tentative) {
    return props.eventData.calendar_color;
  }
  return getAccessibleColor(props.eventData.calendar_color);
});
</script>

<template>
  <div
    class="
      m-auto flex size-[95%] shrink-0 items-center gap-1.5 px-2
      py-0.5 text-sm text-gray-700 hover:shadow-md dark:text-gray-200
    "
    :class="{
      'rounded bg-amber-400/80 dark:text-white': eventData.all_day,
      'h-full rounded border-2': !isMonthView,
    }"
    :style="{
      borderColor: !isMonthView ? eventColor(eventData, false).border : null,
      backgroundColor: eventBackgroundColor,
      color: eventTextColor,
    }"
  >
    <div
      v-if="isMonthView && !eventData.all_day"
      class="mt-0.5 size-2.5 shrink-0 rounded-full"
      :class="{
        'bg-sky-400': !eventData.tentative,
        'border border-dashed border-sky-400/70': eventData.tentative,
      }"
      :style="{
        borderColor: eventData.tentative ? eventData.calendar_color : null,
        backgroundColor: !eventData.tentative ? eventData.calendar_color : null,
        color: !eventData.tentative ? getAccessibleColor(eventData.calendar_color) : null,
      }"
    ></div>
    <div class="grid">
      <div class="truncate rounded">
        {{ label }}
      </div>
    </div>
  </div>
</template>
