<script setup lang="ts">
import { AlertSchemes } from '@/definitions';
import { IconX } from '@tabler/icons-vue';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

import NoticeInfoIcon from '@/tbpro/icons/NoticeInfoIcon.vue';
import NoticeCriticalIcon from '@/tbpro/icons/NoticeCriticalIcon.vue';
import NoticeSuccessIcon from '@/tbpro/icons/NoticeSuccessIcon.vue';
import NoticeWarningIcon from '@/tbpro/icons/NoticeWarningIcon.vue';

const { t } = useI18n();

// component properties
interface Props {
  title: string; // Heading for the alert
  details?: string; // Optional more verbose description for the alert. Togglable.
  canClose?: boolean; // True if the alert can be closed / removed
  scheme?: AlertSchemes; // Type of the alert
}
const props = withDefaults(defineProps<Props>(), {
  canClose: true,
  details: null,
  scheme: AlertSchemes.Error,
});

const emit = defineEmits(['close']);

const isInfo = props.scheme === AlertSchemes.Info;
const isSuccess = props.scheme === AlertSchemes.Success;
const isWarning = props.scheme === AlertSchemes.Warning;
const isError = props.scheme === AlertSchemes.Error;
const hasDetails = props.details !== null;

const open = ref(false);
const toggleDetails = () => {
  open.value = !open.value;
}
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
      <span class="title">
        {{ title }}
      </span>
      <span v-if="hasDetails && open">
        {{ details }}
      </span>
    </span>
    <span class="controls">
      <span v-if="hasDetails" @click="toggleDetails" class="btn-toggle">
        <span v-if="open">Show less</span>
        <span v-if="!open">Show more</span>
      </span>
      <span v-if="canClose" class="btn-close" @click="emit('close')" :title="t('label.close')">
        <icon-x />
      </span>
    </span>
  </div>
</template>


<style scoped>
@import '@/assets/styles/custom-media.pcss';

.notice {
  position: relative;
  border-radius: 0.1875rem;
  gap: 0.625rem;
  border: 0.0625rem solid;
  padding: 0.5625rem 0.5625rem 0.5625rem 2.125rem;
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

.icon {
  position: absolute;
  left: 0.5625rem;
  top: 0.75rem;
}
.body {
  margin: auto;
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  font-size: 0.8125rem;

  .title {
    font-weight: 700;
    line-height: 1.5;
    white-space: pre;
  }
}

.controls {
  position: absolute;
  right: 0.5625rem;
  top: 0.5rem;
  display: flex;
  gap: 1rem;

  .btn-toggle {
    font-size: 0.8125rem;
    text-decoration-line: underline;
    text-underline-offset: 2px;
    cursor: pointer;
  }
  .btn-close {
    cursor: pointer;

    svg {
      stroke: currentColor;
      stroke-width: 1.5;
      width: 1rem;
    }
  }
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
