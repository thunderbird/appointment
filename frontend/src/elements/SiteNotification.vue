<template>
  <a :href="actionUrl">
    <div
      class="
        fixed left-1/2 -translate-x-1/2 my-2.5 p-2 leading-none lg:rounded-full
        flex lg:inline-flex items-center shadow-md dark:shadow-lg
        bg-rose-600 dark:bg-rose-900 text-white shadow-black/30"
      role="alert"
    >
      <span class="flex rounded-full bg-rose-500 dark:bg-rose-800 uppercase px-2 py-1 text-xs font-bold mr-3">
        {{ title }}
      </span>
      <span class="font-semibold mr-2 text-left flex-auto">
        <slot></slot>
      </span>
      <icon-chevron-right class="h-6 w-6 stroke-1 fill-transparent stroke-white-500"/>
    </div>
  </a>
</template>

<script setup>
import { IconChevronRight } from '@tabler/icons-vue';

defineProps({
  title: String,
  actionUrl: String,
});
</script>
