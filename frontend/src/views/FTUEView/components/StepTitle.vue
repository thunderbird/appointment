<script setup lang="ts">
defineProps<{
  title: string;
}>();
</script>

<template>
  <h2>{{ title }}</h2>
</template>

<style scoped>
h2 {
  font-size: 2.25rem;
  font-family: metropolis;
  font-weight: normal;
  letter-spacing: -0.36px;
  line-height: 1.2;
  color: var(--colour-ti-highlight);
  margin: 0 0 1.5rem 0;
}
</style>