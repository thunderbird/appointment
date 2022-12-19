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
    hover:scale-102
    active:scale-98
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
