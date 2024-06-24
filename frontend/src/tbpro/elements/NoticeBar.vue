<script setup>
const props = defineProps({
  type: {
    type: String,
    default: 'info',
  },
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
  }" class="notice">
    <span class="icon">
      <img v-if="isWarning" alt="Warning Icon" src="@/assets/svg/icons/notice-warning.svg"/>
      <img v-if="isError" alt="Error Icon" src="@/assets/svg/icons/notice-error.svg"/>
    </span>
    <slot/>
  </div>
</template>

<style scoped>
.notice {
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 0.1875rem;
  padding: 0.5625rem 1.5rem;
  gap: 0.625rem;
  border: 0.0625rem solid;
}
.info {
  background-color: var(--tbpro-soft);
  border-color: var(--tbpro-primary);
  color: var(--tbpro-primary-pressed);
}
.error {
  background-color: var(--critical-soft);
  border-color: var(--critical-default);
  color: var(--critical-pressed);
}
</style>
