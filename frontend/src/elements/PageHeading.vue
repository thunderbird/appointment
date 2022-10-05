<template>
  <h2 class="flex gap-3">
    <span class="text-4xl font-normal">{{ bold }}</span>
    <span class="text-4xl font-light">{{ light }}</span>
  </h2>
</template>

<script setup>
// component properties
defineProps({
  bold:  String, // first part of heading text
  light: String  // second part of heading text
});
</script>
