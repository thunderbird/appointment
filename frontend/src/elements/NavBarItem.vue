<template>
  <div
    class="flex text-base border-b-4 border-b-transparent transition-all ease-in-out"
    :class="{
      'font-semibold !border-b-teal-500 text-teal-500': active,
      'text-gray-600 dark:text-gray-300 hover:border-b-gray-200 dark:hover:border-b-gray-400': !active,
    }"
  >
    <router-link class="flex justify-center min-w-[120px] items-center" :to="{ name: linkName }">
      {{ label }}
    </router-link>
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
