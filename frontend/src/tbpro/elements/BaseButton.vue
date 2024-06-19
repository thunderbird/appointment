<script setup>
defineProps({
  type: {
    type: String,
    default: 'secondary',
  },
});
</script>

<template>
  <button :class="{'primary': type === 'primary', 'secondary': type === 'secondary'}">
    <span class="icon">
      <slot name="icon"/>
    </span>
    <span class="text">
      <slot/>
    </span>
  </button>
</template>

<style scoped>
.primary {
  background-color: var(--tbpro-primary);
  border-color: var(--tbpro-primary-hover);
  color: var(--neutral);

  &:hover {
    background-color: var(--tbpro-primary-hover);
    border-color: var(--success-pressed);
  }

  &:active {
    background-color: var(--tbpro-primary-pressed);
    border-color: var(--tbpro-primary-pressed);
    box-shadow: none;
  }
}

.secondary {
  background-color: var(--tbpro-secondary);
  border-color: var(--tbpro-secondary-border);
  color: var(--tbpro-text);

  &:hover {
    box-shadow: 0 0.25rem 0.125rem -0.1875rem #0000001A;
  }

  &:active {
    background-color: var(--tbpro-secondary-pressed);
    border-color: var(--tbpro-secondary-pressed-border);
    color: var(--neutral);
  }
}

button {
  display: flex;

  justify-content: center;
  align-items: center;

  border: solid 0.063rem;
  border-radius: 0.188rem; /* 3px */
  box-shadow: 0 0.375rem 0.188rem -0.25rem #152F3C4D;
  font-family: 'Inter', 'sans-serif';
  font-size: 0.813rem; /* 13px */
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
  margin-right: -0.75rem;
}

.text {
  padding: 0.75rem 1.5rem 0.75rem 1.5rem;
}

</style>
