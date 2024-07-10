<script setup lang="ts">
import { eventColor, getAccessibleColor } from '@/utils';
import { computed } from 'vue';

// component properties
const props = defineProps({
  isMonthView: Boolean, // flag, are we in month view?
  event: Object, // the event to show, TODO: use CustomEvent type
  label: String, // event title
});

const eventBackgroundColor = computed(() => {
  if (props.event.all_day) {
    return null;
  }
  if (props.isMonthView || (!props.isMonthView && props.event.tentative)) {
    return 'transparent';
  }
  return props.event.calendar_color;
});

const eventTextColor = computed(() => {
  if (props.isMonthView) {
    return null;
  }
  if (props.event.tentative) {
    return props.event.calendar_color;
  }
  return getAccessibleColor(props.event.calendar_color);
});
</script>

<template>
  <div
    class="
      m-auto flex size-[95%] shrink-0 items-center gap-1.5 px-2
      py-0.5 text-sm text-gray-700 hover:shadow-md dark:text-gray-200
    "
    :class="{
      'rounded bg-amber-400/80 dark:text-white': event.all_day,
      'h-full rounded border-2': !isMonthView,
    }"
    :style="{
      borderColor: !isMonthView ? eventColor(event, false).border : null,
      backgroundColor: eventBackgroundColor,
      color: eventTextColor,
    }"
  >
    <div
      v-if="isMonthView && !event.all_day"
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
