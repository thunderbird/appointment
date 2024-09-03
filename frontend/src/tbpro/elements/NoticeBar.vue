<script setup lang="ts">
import NoticeInfoIcon from '@/tbpro/icons/NoticeInfoIcon.vue';
import NoticeSuccessIcon from '@/tbpro/icons/NoticeSuccessIcon.vue';
import NoticeWarningIcon from '@/tbpro/icons/NoticeWarningIcon.vue';
import NoticeCriticalIcon from '@/tbpro/icons/NoticeCriticalIcon.vue';

// component properties
interface Props {
  type?: string;
};
const props = withDefaults(defineProps<Props>(), {
  type: 'info',
})

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
  background-color: var(--tbpro-soft);
  border-color: var(--tbpro-primary);
  color: var(--tbpro-primary-pressed);
}
.success {
  background-color: var(--success-soft);
  border-color: var(--success);
  color: var(--success-pressed);
}
.warning {
  background-color: var(--warning-background);
  border-color: var(--warning);
  color: var(--yellow-900);
}
.error {
  background-color: var(--critical-soft);
  border-color: var(--critical-default);
  color: var(--critical-pressed);
}

@media (--md) {
  .notice {
    min-width: 31.25rem;
  }
}
</style>
