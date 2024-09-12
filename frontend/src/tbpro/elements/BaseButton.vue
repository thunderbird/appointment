<script setup lang="ts">
import { TooltipPosition } from '@/definitions';
import ToolTip from '@/tbpro/elements/ToolTip.vue';

// component properties
interface Props {
  type?: string;
  size?: string;
  tooltip?: string;
  forceTooltip?: boolean;
}
withDefaults(defineProps<Props>(), {
  type: 'secondary',
  size: 'regular',
  tooltip: '',
  forceTooltip: false,
});
</script>

<template>
  <button :class="{[type]: type, 'small': size === 'small'}" type="button">
    <span class="icon" v-if="$slots?.icon">
      <slot name="icon"/>
    </span>
    <span class="text">
      <slot/>
    </span>
    <tool-tip
      v-if="tooltip"
      class="tooltip"
      :class="{'display-tooltip': forceTooltip}"
      :position="TooltipPosition.Bottom"
      @click.prevent
    >
      {{ tooltip }}
    </tool-tip>
  </button>
</template>

<style scoped>
@import '@/assets/styles/mixins.pcss';

.tooltip {
  transform: translate(0, -100%);
  pointer-events: none;
  opacity: 0;
  transition: opacity 250ms ease-out;
}
button:hover > .tooltip,
.display-tooltip {
  opacity: 1;
}

.primary {
  background-color: var(--colour-service-primary);
  border-color: var(--colour-service-primary-hover);
  color: var(--colour-neutral-base);

  &:hover:enabled {
    background-color: var(--colour-service-primary-hover);
    border-color: var(--colour-success-pressed);
  }

  &:active:enabled {
    background-color: var(--colour-service-primary-pressed);
    border-color: var(--colour-service-primary-pressed);
    box-shadow: none;
  }
}

.secondary {
  background-color: var(--colour-neutral-subtle);
  color: var(--colour-ti-base);

  &:hover:enabled {
    box-shadow: 0 0.25rem 0.125rem -0.1875rem #0000001A;
  }

  &:active:enabled {
    background-color: var(--colour-neutral-border);
    border-color: var(--colour-neutral-border);
  }
}

.link {
  background-color: transparent;
  color: var(--colour-service-primary);
  text-decoration: underline;
  box-shadow: none;
  border: none !important;

  .text {
    padding: 0;
    user-select: all;
    font-weight: 600;
    line-height: 1;
  }
}

button {
  --colour-btn-border: var(--colour-neutral-border);
  display: flex;

  justify-content: center;
  align-items: center;

  border-radius: var(--border-radius);
  @mixin faded-border var(--colour-btn-border);
  box-shadow: 0 0.375rem 0.188rem -0.25rem #152F3C4D;
  font-family: 'Inter', 'sans-serif';
  font-size: var(--txt-input); /* 13px */
  line-height: 0.983rem; /* 15.73px */
  font-weight: 700;

  min-width: 8.0rem;

  transition: all 250ms ease-out;

  cursor: pointer;

  &:hover {
    box-shadow: 0 0.25rem 0.125rem -0.1875rem #0000001A;
  }

  &:active {
    box-shadow: none;
    outline: none !important;
  }

  &:focus {
    outline: 0.125rem solid var(--colour-service-primary);
    outline-offset: 0.0625rem;
    box-shadow: none;
  }

  &:disabled {
    background-color: var(--colour-neutral-border);
    border-color: var(--colour-neutral-border);
    color: var(--colour-ti-muted);
    box-shadow: none;
    cursor: not-allowed;
  }
}

.icon {
  display: flex;
  align-items: center;
  height: 100%;

  padding-left: 0.75rem;
  padding-right: 0.75rem;
  margin-right: -0.75rem;
}

.text {
  user-select: none;
  padding: 0.75rem 1.5rem 0.75rem 1.5rem;
}

.small {
  .text {
    text-transform: uppercase;
    font-size: 0.5625rem;
    padding: 0.5625rem;
    font-weight: 700;
  }

  &button {
    min-width: initial;
    height: 1.25rem
  }
}

</style>
