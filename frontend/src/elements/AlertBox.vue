<template>
<div
  class="
    p-2 leading-none lg:rounded-full flex lg:inline-flex items-center shadow-md dark:shadow-lg
    text-white shadow-black/30"
  role="alert"
  :class="{
    'bg-rose-600 dark:bg-rose-900': scheme === alertSchemes.error,
    'bg-orange-400 dark:bg-orange-700': scheme === alertSchemes.warning,
    'bg-green-400 dark:bg-green-700': scheme === alertSchemes.success,
    'bg-teal-400 dark:bg-teal-700': scheme === alertSchemes.info,
  }"
>
  <span class="flex rounded-full uppercase px-2 py-1 text-center text-xs font-bold mr-3"
    :class="{
      'bg-rose-500 dark:bg-rose-800': scheme === alertSchemes.error,
      'bg-orange-500 dark:bg-orange-800': scheme === alertSchemes.warning,
      'bg-green-500 dark:bg-green-800': scheme === alertSchemes.success,
      'bg-teal-500 dark:bg-teal-800': scheme === alertSchemes.info,
    }"
        v-if="title"
  >
    {{ title }}
  </span>
  <span class="block sm:inline ml-1">
    <slot></slot>
  </span>
  <span class="ml-auto" @click="emit('close')">
    <icon-x class="h-6 w-6 stroke-1 fill-transparent stroke-white cursor-pointer" />
  </span>
</div>
</template>

<script setup>
import { IconX } from '@tabler/icons-vue';
import { alertSchemes } from '@/definitions';

defineProps({
  title: String,
  scheme: {
    type: Number,
    default: alertSchemes.error,
  },
});

const emit = defineEmits(['close']);

</script>
