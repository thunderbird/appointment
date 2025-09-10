<script setup lang="ts">
interface Props {
  title: string;
}
defineProps<Props>();
</script>

<template>
  <div class="info-box-container">
    <header>
      <h3>{{ title }}</h3>
    </header>
    <div class="info-box-container-content">
      <p><slot></slot></p>
    </div>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.info-box-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  margin-block-end: 5rem;
  border-block-start: 1px solid var(--colour-neutral-border);

  header {
    display: flex;
    gap: 1rem;
    margin: 1rem;
    height: 4rem;
  }

  h3 {
    margin-block: auto;
    font-size: 1.5rem;
    line-height: 2rem;
    color: var(--colour-apmt-secondary);
  }

  p {
    font-size: 1.125rem;
    line-height: 2;
  }

  .info-box-container-content {
    margin: 1rem;
    margin-block-end: 2rem;
  }
}

@media (--md) {
  .info-box-container {
    width: 33.33%;
  }
}
</style>
