<script setup lang="ts">
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
</script>

<template>
  <svg :aria-label="t('icons.critical')" class="tbpro-critical-icon" width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path opacity="0.2" d="M8 1C7.34694 1.00095 6.778 1.45312 6.5 2L1.324 11.4609C1 12 1.00152 12.1118 1 12.5C1 13.3284 1.67157 14 2.5 14H13.5C14.3284 14 15 13.3284 15 12.5C15 12.106 15 12 14.668 11.4473L9.5 2C9.218 1.44727 8.65609 1.00005 8 1Z" fill="none" class="tbpro-icon-background"/>
    <path d="M8 1C7.34694 1.00095 6.778 1.45312 6.5 2L1.324 11.4609C1 12 1.00152 12.1118 1 12.5C1 13.3284 1.67157 14 2.5 14H13.5C14.3284 14 15 13.3284 15 12.5C15 12.106 15 12 14.668 11.4473L9.5 2C9.218 1.44727 8.65609 1.00005 8 1Z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M8 5V9" stroke="currentColor" stroke-linecap="round"/>
    <path d="M8.00001 11C8.00001 11 8.00001 11 8 11C8 11 8 11 8 11C8 11 8 11 8 11C8.00001 11 8.00001 11 8.00001 11Z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
</template>

<style scoped>
.tbpro-critical-icon {
  color: var(--colour-danger-default);

  .tbpro-icon-background {
    color: var(--colour-danger-pressed);
  }
}
</style>
