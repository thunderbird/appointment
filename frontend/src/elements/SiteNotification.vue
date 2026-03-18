<script setup lang="ts">
import { PhCaretRight } from '@phosphor-icons/vue';

// component properties
interface Props {
  title: string,
  actionUrl: string,
}
defineProps<Props>();
</script>

<template>
  <a :href="actionUrl">
    <div class="notification-wrapper" role="alert">
      <span class="notification-title">
        {{ title }}
      </span>
      <span class="notification-text">
        <slot></slot>
      </span>
      <ph-caret-right />
    </div>
  </a>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.notification-wrapper {
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  z-index: 19999;
  margin-top: 0.625rem;
  margin-bottom: 0.625rem;
  padding: .5rem;
  border-radius: .5rem;

  display: flex;
  flex-direction: column;
  align-items: center;
  gap: .75rem;

  line-height: 1;
  color: var(--colour-ti-base-dark);
  background-color: var(--colour-danger-hover);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);

  .notification-title {
    border-radius: .25rem;
    background-color: var(--colour-ti-critical);
    text-transform: uppercase;
    padding: .25rem .5rem;
    font-size: 0.75rem;
    font-weight: bold;
    line-height: 1rem;
  }

  .notification-text {
    flex: 1 1 auto;
    font-weight: 600;
  }
}

@media (--lg) {
  .notification-wrapper {
    flex-direction: row;
  }
}
</style>
