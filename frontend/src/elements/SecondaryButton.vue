<template>
  <button class="
    h-10
    text-xl
    font-semibold
    whitespace-nowrap
    text-gray-600
    bg-white
    border
    border-teal-500
    rounded-full
    hover:shadow-md
    hover:scale-105
    active:scale-95
    disabled:from-teal-200
    disabled:to-sky-300
    px-6
    transition-all
    ease-in-out
  ">
    {{ label }}
  </button>
</template>

<script setup>
// component properties
defineProps({
  label: String // button text
});
</script>
