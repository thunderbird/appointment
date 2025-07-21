<script setup lang="ts">
import {
  NoticeInfoIcon, NoticeCriticalIcon, NoticeSuccessIcon, NoticeWarningIcon
} from '@thunderbirdops/services-ui';

// component properties
interface Props {
  type?: string;
}
const props = withDefaults(defineProps<Props>(), {
  type: 'info',
});

const isInfo = props.type === 'info';
const isSuccess = props.type === 'success;';
const isWarning = props.type === 'warning';
const isError = props.type === 'error';
</script>

<template>
  <div :class="{
    error: isError,
    info: isInfo,
    warning: isWarning,
    success: isSuccess
  }" class="notice notice-bar">
    <span class="icon">
      <notice-info-icon v-if="isInfo"/>
      <notice-success-icon v-if="isSuccess"/>
      <notice-warning-icon v-if="isWarning"/>
      <notice-critical-icon v-if="isError"/>
    </span>
    <span class="body">
      <slot/>
    </span>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.icon {
  position: absolute;
  left: 0.5625rem;
  margin-top: auto;
  margin-bottom: auto;
}
.body {
  margin: auto;
  font-size: 0.8125rem;
  font-weight: 700;
  line-height: 1;
  white-space: pre;
}
.notice {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 0.1875rem;
  gap: 0.625rem;
  border: 0.0625rem solid;
  padding: 0.5625rem 0.5625rem 0.5625rem 1.75rem;
}
.info {
  background-color: var(--colour-service-soft);
  border-color: var(--colour-service-primary);
  color: var(--colour-service-primary-pressed);
}
.success {
  background-color: var(--colour-success-soft);
  border-color: var(--colour-success-default);
  color: var(--colour-ti-success);
}
.warning {
  background-color: var(--colour-warning-soft);
  border-color: var(--colour-warning-default);
  color: var(--colour-ti-warning);
}
.error {
  background-color: var(--colour-danger-soft);
  border-color: var(--colour-danger-default);
  color: var(--colour-danger-pressed);
}

.dark {
  .info {
    color: var(--colour-service-accent-1);
    border-color: var(--colour-service-accent-1);
  }
}

@media (--md) {
  .notice {
    min-width: 31.25rem;
  }
}
</style>
