<script setup lang="ts">
import { PhInfo } from '@phosphor-icons/vue';

// component properties
interface Props {
  message?: string;
  showIcon?: boolean;
}
withDefaults(defineProps<Props>(), {
  message: null,
  showIcon: false,
});
</script>

<template>
  <div class="container">
    <p v-if="message" class="message">
      <ph-info v-if="showIcon" class="icon" aria-hidden="true"/>
      {{ message }}
    </p>
    <slot></slot>
  </div>
</template>

<style scoped>
.container {
  background: var(--colour-neutral-border);
  border-radius: .75rem;
  width: 100%;
  /* height: 7rem; */
  text-align: center;
  padding: 1rem 2rem;

  .message {
    font-weight: 500;
    font-size: .875rem;
    margin-bottom: 1rem;
  }

  .icon {
    width: 1rem;
    display: inline;
    margin: 0 .25rem 0 .125rem;
  }
}
</style>
