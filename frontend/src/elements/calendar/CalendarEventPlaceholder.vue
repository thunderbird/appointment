<template>
  <div
    class="m-auto size-[95%] shrink-0 text-sm text-gray-700 hover:shadow-md dark:text-gray-200"
    :class="{
      'group/event cursor-pointer rounded-md p-1 hover:bg-gradient-to-b hover:shadow-lg': !isBusy,
      'bg-teal-50 hover:from-teal-500 hover:to-sky-600 hover:!text-white dark:bg-teal-800': !isBusy,
      'bg-gradient-to-b from-teal-500 to-sky-600 shadow-lg': isSelected,
      'h-full rounded': !isMonthView,
      '!cursor-not-allowed rounded-md bg-gray-100 p-1 dark:bg-gray-600': isBusy,
    }"
  >
    <div class="grid">
      <div
        class="
          truncate rounded h-full p-1 font-semibold border-2 border-dashed 
          border-teal-500 group-hover/event:border-white"
        :class="{
          '!border-none': isBusy,
          'border-white': isSelected,
        }"
      >
        <template v-if="isBusy">{{ t('label.busy') }}</template>
        <template v-else>{{ label }}</template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

// component properties
const props = defineProps({
  isBusy: Boolean, // flag showing this event as busy and non-selectable
  isSelected: Boolean, // flag showing if the event is currently selected by user
  isMonthView: Boolean, // flag, are we in month view?
  label: String, // event title
});

</script>
