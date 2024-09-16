<script setup lang="ts">
import { inject } from 'vue';
import { dayjsKey } from '@/keys';

const dj = inject(dayjsKey);

// component properties
interface Props {
  day: string; // number of day in its month
  isActive: boolean; // flag showing if the day belongs to active month
  isSelected: boolean; // flag showing if the day is currently selected by user
  isToday: boolean; // flag showing if the day is today
  placeholder: boolean; // flag formating events as placeholder
  hasEvents: boolean; // if true show event indicator
  showDetails: boolean; // flag enabling event popups with details
  popupPosition?: string; // currently supported: right, left, top
  disabled?: boolean; // flag making this day non-selectable and inactive
}
defineProps<Props>();

</script>

<template>
  <div
    class="group/day cursor-pointer px-1 py-2"
    :class="{
      'bg-white dark:bg-gray-700': isActive,
      'bg-gray-50 text-gray-400 dark:bg-gray-600': !isActive || disabled,
      'cursor-not-allowed': disabled
    }"
  >
    <div
      class="relative mx-auto w-6 rounded-full text-center"
      :class="{
        'bg-teal-500 font-semibold text-white': isToday,
        'text-teal-500': isSelected && !isToday,
        'group-hover/day:bg-sky-600': isToday && !disabled,
        'group-hover/day:text-sky-600': !isToday && !disabled,
      }"
    >
      {{ dj(day).format('D') }}
      <div v-if="hasEvents" class="absolute -bottom-1 left-1/2 size-1.5 -translate-x-1/2 rounded-full bg-teal-600"></div>
    </div>
  </div>
</template>
