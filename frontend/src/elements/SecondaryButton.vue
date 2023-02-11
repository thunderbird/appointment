<template>
  <button
    class="
      relative h-10 text-xl font-semibold whitespace-nowrap border rounded-full hover:shadow-md hover:scale-102 active:scale-98 px-6 transition-all ease-in-out
      text-gray-600 bg-white border-teal-500 disabled:from-teal-200 disabled:to-sky-300
    "
    :class="{ '!text-transparent': waiting }"
  >
    <div v-if="waiting" class="absolute w-5 h-5 animate-spin rounded-full border-2 border-teal-500 border-t-transparent"></div>
    {{ label }}
  </button>
</template>

<script setup>
// component properties
defineProps({
  label:   String,  // button text
  waiting: Boolean, // if true, spinning animation is shown instead of label
});
</script>
