<template>
  <button
    class="
      relative h-10 text-base font-semibold whitespace-nowrap rounded-full bg-gradient-to-br hover:shadow-md
      hover:scale-102 active:scale-98 disabled:scale-100 disabled:shadow-none disabled:opacity-50 px-6
      transition-all ease-in-out flex items-center justify-center gap-2
      text-white from-rose-400 to-rose-600 dark:from-rose-600 dark:to-rose-900 shadow-black
      enabled:hover:from-rose-600 enabled:hover:to-rose-600
    "
    :class="{ 'text-transparent': waiting }"
  >
    <div
      v-if="waiting"
      class="absolute w-5 h-5 animate-spin rounded-full border-2 border-white border-t-transparent"
    ></div>
    <icon-copy v-if="icon === 'copy'" class="h-6 w-6 stroke-2 stroke-current fill-transparent" />
    <icon-check v-if="icon === 'check'" class="h-6 w-6 stroke-2 stroke-current fill-transparent" />
    {{ label }}
  </button>
</template>

<script setup>
// icons
import {
  IconCheck,
  IconCopy,
} from '@tabler/icons-vue';

// component properties
defineProps({
  label: String, // button text
  icon: String, // optional icon displayed before label
  waiting: Boolean, // if true, spinning animation is shown instead of label
});
</script>
