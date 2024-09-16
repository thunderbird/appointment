<script setup lang="ts">
// icons
import { IconCheck, IconCopy } from '@tabler/icons-vue';

// component properties
interface Props {
  label?: string; // button text
  icon?: 'copy'|'check'; // optional icon displayed before label
  waiting?: boolean; // if true, spinning animation is shown instead of label
}
defineProps<Props>();
</script>

<template>
  <button
    class="
      relative flex h-10 items-center justify-center gap-2 whitespace-nowrap rounded-full
      bg-gradient-to-br from-rose-400 to-rose-600 px-6 text-base font-semibold
      text-white shadow-black transition-all ease-in-out hover:scale-102 hover:shadow-md
      active:scale-98 enabled:hover:from-rose-600 enabled:hover:to-rose-600 disabled:scale-100 disabled:opacity-50 disabled:shadow-none
      dark:from-rose-600 dark:to-rose-900
    "
    :class="{ '!text-transparent': waiting }"
  >
    <div
      v-if="waiting"
      class="absolute size-5 animate-spin rounded-full border-2 border-white border-t-transparent"
    ></div>
    <icon-copy v-if="icon === 'copy'" class="size-6 fill-transparent stroke-current stroke-2" />
    <icon-check v-if="icon === 'check'" class="size-6 fill-transparent stroke-current stroke-2" />
    <template v-if="label">
      {{ label }}
    </template>
    <template v-else>
      <slot></slot>
    </template>
  </button>
</template>
