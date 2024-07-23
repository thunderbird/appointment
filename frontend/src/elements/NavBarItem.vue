<script setup lang="ts">
// component properties
interface Props {
  active: boolean; // indicator for currently active item
  label: string; // item text label
  linkName: string; // name of the route link target
};
defineProps<Props>();
</script>

<template>
  <div
    class="group relative flex text-base font-medium"
    :class="{ 'text-gray-600 dark:text-gray-300': !active }"
  >
    <router-link class="flex min-w-[120px] items-center justify-center" :to="{ name: linkName }">
      {{ label }}
    </router-link>
    <div
      class="absolute bottom-0 h-1 w-full rounded bg-transparent transition-colors ease-in-out"
      :class="{
        'bg-gradient-to-r from-teal-500 to-sky-500': active,
        'group-hover:bg-gray-200 group-hover:dark:bg-gray-400': !active,
      }"
    ></div>
  </div>
</template>
