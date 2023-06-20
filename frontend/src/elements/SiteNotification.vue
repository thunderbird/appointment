<template>
<div class="bg-transparent text-center py-2 fixed left-0 right-0">
  <div
      class="p-2 bg-red-900 items-center text-indigo-100
             leading-none lg:rounded-full flex lg:inline-flex"
      role="alert">
    <span class="flex rounded-full bg-red-800 uppercase px-2 py-1 text-xs font-bold mr-3">{{ title }}</span>
    <span class="font-semibold mr-2 text-left flex-auto"><slot></slot></span>
    <a :href="actionUrl">
      <icon-chevron-right class="h-6 w-6 stroke-1 fill-transparent stroke-white-500 cursor-pointer"/>
    </a>
  </div>
</div>
</template>

<script setup>
import { IconChevronRight } from '@tabler/icons-vue';

defineProps({
  title: String,
  actionUrl: String,
});
</script>
