<template>
  <div
    class="group/day px-1 cursor-pointer py-2"
    :class="{
      'bg-white dark:bg-gray-700': isActive,
      'bg-gray-50 text-gray-400 dark:bg-gray-600': !isActive || disabled,
      'cursor-not-allowed': disabled
    }"
  >
    <div
      class="relative w-6 rounded-full text-center mx-auto"
      :class="{
        'bg-teal-500 font-semibold text-white': isToday,
        'text-teal-500': isSelected && !isToday,
        'group-hover/day:bg-sky-600': isToday && !disabled,
        'group-hover/day:text-sky-600': !isToday && !disabled,
      }"
    >
      {{ dj(day).format('D') }}
      <div v-if="events" class="absolute -bottom-1 left-1/2 size-1.5 -translate-x-1/2 rounded-full bg-teal-600"></div>
    </div>
  </div>
</template>

<script setup>
import { inject } from 'vue';

const dj = inject('dayjs');

// component properties
const props = defineProps({
  day: String, // number of day in its month
  isActive: Boolean, // flag showing if the day belongs to active month
  isSelected: Boolean, // flag showing if the day is currently selected by user
  isToday: Boolean, // flag showing if the day is today
  placeholder: Boolean, // flag formating events as placeholder
  events: Array, // list of events to show on this day or null
  showDetails: Boolean, // flag enabling event popups with details
  popupPosition: String, // currently supported: right, left, top
  disabled: Boolean, // flag making this day non-selectable and inactive
});

// component emits
const emit = defineEmits(['eventSelected']);
</script>
