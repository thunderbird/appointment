<template>
<div
  class="
    p-2 leading-none lg:rounded-full flex lg:inline-flex items-center shadow-md dark:shadow-lg
    text-white shadow-black/30"
  role="alert"
  :class="{
    hidden: isHidden,
    'bg-rose-600 dark:bg-rose-900': isError,
    'bg-orange-400 dark:bg-orange-700': isAlert,
  }"
>
  <span class="flex rounded-full uppercase px-2 py-1 text-xs font-bold mr-3"
    :class="{
      'bg-rose-500 dark:bg-rose-800': isError,
      'bg-orange-500 dark:bg-orange-800': isAlert,
    }"
  >
    {{ title }}
  </span>
  <span class="block sm:inline ml-1">
    <slot></slot>
  </span>
  <span class="ml-auto place-self-start" @click="onClose">
    <icon-x class="h-6 w-6 stroke-1 fill-transparent stroke-white cursor-pointer" />
  </span>
</div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { IconX } from '@tabler/icons-vue';

const props = defineProps({
  title: String,
  scheme: {
    type: String,
    default: 'error',
  },
});

const isError = computed(() => props.scheme === 'error');
const isAlert = computed(() => props.scheme === 'alert');

const isHidden = ref(false);
const onClose = () => { isHidden.value = true; };

</script>
