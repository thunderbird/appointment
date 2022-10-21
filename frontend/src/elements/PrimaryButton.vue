<template>
  <button class="
    h-10
    text-xl
    font-semibold
    text-white
    rounded-full
    bg-gradient-to-br
    from-teal-400
    to-sky-600
    hover:from-sky-400
    hover:to-teal-600
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
