<template>
  <div
    class="relative group flex font-medium text-base"
    :class="{ 'text-gray-600 dark:text-gray-300': !active }"
  >
    <router-link class="flex justify-center min-w-[120px] items-center" :to="{ name: linkName }">
      {{ label }}
    </router-link>
    <div
      class="absolute rounded bottom-0 h-1 w-full bg-transparent transition-colors ease-in-out"
      :class="{
        'bg-gradient-to-r from-teal-500 to-sky-500': active,
        'group-hover:bg-gray-200 group-hover:dark:bg-gray-400': !active,
      }"
    ></div>
  </div>
</template>

<script setup>
// component properties
defineProps({
  active: Boolean,  // indicator for currently active item
  label: String,    // item text label
  linkName: String, // name of the route link target
});
</script>
