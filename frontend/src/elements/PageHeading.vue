<template>
  <h2 class="flex gap-3">
    <span class="text-4xl">{{ bold }}</span>
    <span class="text-4xl font-light">{{ light }}</span>
  </h2>
</template>

<script setup>
// inherited properties
defineProps({
  bold: String,
  light: String
});
</script>
