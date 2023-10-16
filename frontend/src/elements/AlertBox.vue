<template>
<div
  class="
    p-2 leading-none lg:rounded-full flex lg:inline-flex items-center shadow-md dark:shadow-lg
    text-white shadow-black/30"
  role="alert"
  :class="{ hidden: isHidden, 'error-title': scheme === 'error', 'alert-title': scheme === 'alert' }"
>
  <span class="flex rounded-full uppercase px-2 py-1 text-xs font-bold mr-3"
    :class="{ 'error-body': scheme === 'error', 'alert-body': scheme === 'alert' }"
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
import { ref } from 'vue';
import { IconX } from '@tabler/icons-vue';

defineProps({
  title: String,
  scheme: {
    type: String,
    default: 'error',
  },
});

const isHidden = ref(false);
const onClose = () => { isHidden.value = true; };

</script>

<style scoped>
  .error-title {
    @apply bg-rose-600 dark:bg-rose-900;
  }
  .error-body {
    @apply bg-rose-500 dark:bg-rose-800;
  }
  .alert-title {
    @apply bg-orange-400 dark:bg-orange-700;
  }
  .alert-body {
    @apply bg-orange-500 dark:bg-orange-800;
  }
</style>
