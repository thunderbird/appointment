<template>
<div
  class="
    p-2 leading-none lg:rounded-full flex lg:inline-flex items-center shadow-md dark:shadow-lg
    bg-rose-600 dark:bg-rose-900 text-white shadow-black/30"
  role="alert"
  :class="{ hidden: isHidden }"
>
  <span class="flex rounded-full bg-rose-500 dark:bg-rose-800 uppercase px-2 py-1 text-xs font-bold mr-3">
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
import { ref } from 'vue';
import { IconX } from '@tabler/icons-vue';

defineProps({
  title: String,
});

const isHidden = ref(false);
const onClose = () => { isHidden.value = true; };
</script>
