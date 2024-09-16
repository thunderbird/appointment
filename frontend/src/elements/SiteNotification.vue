<script setup lang="ts">
import { IconChevronRight } from '@tabler/icons-vue';

// component properties
interface Props {
  title: string,
  actionUrl: string,
}
defineProps<Props>();
</script>

<template>
  <a :href="actionUrl">
    <div
      class="fixed left-1/2 z-[999] my-2.5 flex -translate-x-1/2 items-center bg-rose-600 p-2 leading-none text-white shadow-md shadow-black/30 dark:bg-rose-900 dark:shadow-lg lg:inline-flex lg:rounded-full"
      role="alert"
    >
      <span class="mr-3 flex rounded-full bg-rose-500 px-2 py-1 text-xs font-bold uppercase dark:bg-rose-800">
        {{ title }}
      </span>
      <span class="mr-2 flex-auto text-left font-semibold">
        <slot></slot>
      </span>
      <icon-chevron-right class="stroke-white-500 size-6 fill-transparent stroke-1"/>
    </div>
  </a>
</template>
