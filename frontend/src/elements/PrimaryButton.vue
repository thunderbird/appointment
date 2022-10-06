<template>
  <button class="text-xl font-semibold text-white rounded-full bg-gradient-to-br from-teal-400 to-cyan-700 px-6 transition-all ease-in-out">
    {{ label }}
  </button>
</template>

<script setup>
// component properties
defineProps({
  label: String // button text
});
</script>
