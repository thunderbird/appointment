<template>
  <button
    class="
      relative h-10 text-xl font-semibold whitespace-nowrap border rounded-full px-6 transition-all ease-in-out
      hover:shadow-md hover:scale-102 active:scale-98 disabled:scale-100 disabled:shadow-none disabled:opacity-50
      text-gray-600 dark:text-gray-400 bg-white dark:bg-gray-700 border-teal-500
    "
    :class="{ '!text-transparent': waiting }"
  >
    <div
      v-if="waiting"
      class="absolute w-5 h-5 animate-spin rounded-full border-2 border-teal-500 border-t-transparent"
    ></div>
    {{ label }}
  </button>
</template>

<script setup>
// component properties
defineProps({
  label: String, // button text
  waiting: Boolean, // if true, spinning animation is shown instead of label
});
</script>
