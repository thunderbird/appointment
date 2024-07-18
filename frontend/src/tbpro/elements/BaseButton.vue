<script setup>
import { tooltipPosition } from '@/definitions';
import ToolTip from '@/tbpro/elements/ToolTip.vue';

defineProps({
  type: {
    type: String,
    default: 'secondary',
  },
  size: {
    type: String,
    default: 'regular',
  },
  tooltip: {
    type: String,
    default: '',
  },
  forceTooltip: {
    type: Boolean,
    default: false,
  },
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
      :position="tooltipPosition.bottom"
      @click.prevent
    >
      {{ tooltip }}
    </tool-tip>
  </button>
</template>
<style scoped>
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
  background-color: var(--tbpro-primary);
  border-color: var(--tbpro-primary-hover);
  color: var(--neutral);

  &:hover:enabled {
    background-color: var(--tbpro-primary-hover);
    border-color: var(--success-pressed);
  }

  &:active:enabled {
    background-color: var(--tbpro-primary-pressed);
    border-color: var(--tbpro-primary-pressed);
    box-shadow: none;
  }
}

.secondary {
  background-color: var(--tbpro-secondary);
  border-color: var(--tbpro-secondary-border);
  color: var(--tbpro-text);

  &:hover:enabled {
    box-shadow: 0 0.25rem 0.125rem -0.1875rem #0000001A;
  }

  &:active:enabled {
    background-color: var(--tbpro-secondary-pressed);
    border-color: var(--tbpro-secondary-pressed-border);
    color: var(--neutral);
  }
}

.link {
  background-color: transparent;
  color: var(--tbpro-primary);
  text-decoration: underline;
  box-shadow: none;
  border: none;

  .text {
    padding: 0;
    user-select: all;
    font-weight: 400;
    line-height: 1;
  }
}

button {
  display: flex;

  justify-content: center;
  align-items: center;

  border: solid 0.063rem;
  border-radius: var(--border-radius);
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
    outline: 0.125rem solid var(--tbpro-primary);
    outline-offset: 0.0625rem;
    box-shadow: none;
  }

  &:disabled {
    background-color: var(--tbpro-disabled);
    border-color: var(--tbpro-disabled);
    color: var(--tbpro-text-muted);
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
