<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router';
import { PhArrowRight, PhWarningCircle } from '@phosphor-icons/vue';

defineProps<{
  label: string;
  to?: RouteLocationRaw;
  showWarning?: boolean;
  showArrow?: boolean;
  testId?: string;
}>();

defineEmits<{
  click: [];
}>();
</script>

<script lang="ts">
export default {
  name: 'AsideNavButton',
};
</script>

<template>
  <router-link
    v-if="to"
    :to="to"
    class="aside-nav-button"
    :data-testid="testId"
  >
    <slot name="icon">
      <ph-warning-circle
        v-if="showWarning"
        class="warning-icon"
        weight="fill"
      />
    </slot>

    <span class="label">{{ label }}</span>

    <ph-arrow-right
      v-if="showArrow !== false"
      class="arrow-icon"
      size="16"
    />
  </router-link>

  <button
    v-else
    type="button"
    class="aside-nav-button"
    :data-testid="testId"
    @click="$emit('click')"
  >
    <slot name="icon">
      <ph-warning-circle
        v-if="showWarning"
        class="warning-icon"
        weight="fill"
      />
    </slot>

    <span class="label">{{ label }}</span>

    <ph-arrow-right
      v-if="showArrow !== false"
      class="arrow-icon"
      size="16"
    />
  </button>
</template>

<style scoped>
.aside-nav-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  background-color: var(--colour-neutral-base);
  border: 1px solid transparent;
  box-shadow: 0.1875rem 0.1875rem 1rem 0 var(--shadow-surface-default);
  height: 3rem;
  font-size: 0.875rem;
  line-height: 1.23;
  font-weight: 400;
  color: var(--colour-ti-secondary);
  text-align: start;
  width: 100%;
  text-decoration: none;
  cursor: pointer;

  &:hover {
    background-color: var(--colour-primary-soft);
    border-color: var(--colour-neutral-border);
    box-shadow:
      0.0625rem 0.0625rem 0 0 var(--shadow-surface-interactive-outer),
      inset 0.125rem 0.125rem 0.25rem 0 var(--shadow-surface-interactive-inset);
    color: var(--colour-ti-base);
    text-decoration: none;

    .arrow-icon {
      color: var(--colour-ti-base);
    }

    .warning-icon {
      color: var(--colour-danger-default);
    }
  }

  &:focus-visible {
    background-color: var(--colour-primary-soft);
    border-color: var(--colour-neutral-border);
    box-shadow:
      0.0625rem 0.0625rem 0 0 var(--shadow-surface-interactive-outer),
      inset 0.125rem 0.125rem 0.25rem 0 var(--shadow-surface-interactive-inset);
    color: var(--colour-ti-base);
    outline: 0.125rem solid var(--colour-primary-default);
    outline-offset: 0.125rem;

    .warning-icon {
      color: var(--colour-danger-default);
    }
  }

  &:active {
    background-color: color-mix(in srgb, var(--colour-primary-default) 20%, transparent);
    border-color: var(--colour-neutral-border);
    box-shadow:
      0.0625rem 0.0625rem 0 0 var(--shadow-surface-interactive-outer),
      inset 0.125rem 0.125rem 0.25rem 0 var(--shadow-surface-interactive-inset);
    color: var(--colour-ti-base);

    .warning-icon {
      color: var(--colour-danger-default);
    }
  }

  .label {
    flex: 1 1 0;
    min-width: 0;
    text-transform: lowercase;

    &::first-letter {
      text-transform: uppercase;
    }
  }

  .warning-icon {
    color: var(--colour-danger-default);
    width: 1.5rem;
    height: 1.5rem;
    flex-shrink: 0;
  }

  :deep(.icon-left) {
    color: var(--colour-ti-highlight);
    width: 1.5rem;
    height: 1.5rem;
    flex-shrink: 0;
  }

  .arrow-icon {
    flex-shrink: 0;
    color: inherit;
  }
}
</style>
