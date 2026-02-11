<script setup lang="ts">
defineProps<{
  title: string;
  description: string;
  iconSrc: string;
  iconAlt: string;
  showDescription?: boolean;
}>();
</script>

<template>
  <button>
    <img :src="iconSrc" :alt="iconAlt" :title="iconAlt"/>

    <div>
      <h3>{{ title }}</h3>
      <p v-if="showDescription">{{ description }}</p>
    </div>
  </button>
</template>

<style scoped>
button {
  display: flex;
  gap: 1.5rem;
  padding: 1rem;
  box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.12);
  border-radius: 0.5rem;
  text-align: left;
  align-items: center;
  width: 100%;

  img { 
    width: 2.25rem;
    height: 2.25rem;
  }

  h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--colour-ti-base);
    margin-block-end: 0.5rem;
  }

  p {
    margin-block-end: 0;
  }

  &:hover {
    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.12);
  }
}
</style>