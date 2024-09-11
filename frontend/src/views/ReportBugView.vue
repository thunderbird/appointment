<script setup lang="ts">
import { onMounted } from 'vue';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';

const redirect = async () => {
  window.location = import.meta.env?.VITE_REPORT_BUG_URL ?? '/';
};

onMounted(() => {
  redirect();
});
</script>
<template>
  <div class="full-page">
    <loading-spinner/>
  </div>
</template>
<style scoped>
  @import '@/assets/styles/mixins.pcss';
  .full-page {
    @mixin faded-background var(--colour-neutral-border);

    position: fixed;
    display: flex;
    justify-content: center;
    align-items: center;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 50;
  }
</style>
