<template>
<div
  class="flex items-center p-2 leading-none text-white shadow-md shadow-black/30 dark:shadow-lg lg:inline-flex lg:rounded-xl"
  role="alert"
  :class="{
    'bg-rose-600 dark:bg-rose-900': scheme === alertSchemes.error,
    'bg-orange-400 dark:bg-orange-700': scheme === alertSchemes.warning,
    'bg-green-400 dark:bg-green-700': scheme === alertSchemes.success,
    'bg-teal-400 dark:bg-teal-700': scheme === alertSchemes.info,
  }"
>
  <span class="mr-3 flex rounded-full px-2 py-1 text-center text-xs font-bold uppercase"
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
  <span class="ml-1 block sm:inline">
    <slot></slot>
  </span>
  <span v-if="canClose" class="btn-close ml-auto" @click="emit('close')" :title="t('label.close')">
    <icon-x class="size-6 cursor-pointer fill-transparent stroke-white stroke-1" />
  </span>
</div>
</template>

<script setup>
import { IconX } from '@tabler/icons-vue';
import { alertSchemes } from '@/definitions';

defineProps({
  title: String,
  canClose: {
    type: Boolean,
    default: true,
  },
  scheme: {
    type: Number,
    default: alertSchemes.error,
  },
});

const emit = defineEmits(['close']);

</script>
