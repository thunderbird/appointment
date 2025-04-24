<script setup lang="ts">
import { SelectOption } from '@/models';

// component properties
interface Props {
  options: SelectOption[];
  required: boolean;
  disabled?: boolean;
}

withDefaults(defineProps<Props>(), {
  required: false,
  disabled: false,
});

const model = defineModel<(string | number)[]>({ default: [] });

/**
 * Adds or removes the option value from the model.
 * There's probably a better way to do this lol!
 * @param option
 */
const toggleBubble = (option: SelectOption) => {
  // Detect what our current state is
  const val = model.value.indexOf(option.value);

  if (val > -1) {
    // We have the value, so filter it out
    model.value = model.value.filter((value) => option.value !== value);
  } else {
    // We don't have the value, so mix it in
    model.value = [
      ...model.value,
      option.value,
    ];
  }

  // Sort for niceness
  model.value.sort();
};
</script>

<template>
  <div class="wrapper">
    <label>
      <span class="label">
        <slot/>
        <span v-if="required && model?.length === 0" class="required">*</span>
      </span>
    </label>
    <ul class="bubble-list">
      <li v-for="option in options" :key="option.value">
        <button
          class="tbpro-bubble"
          :aria-pressed="model.indexOf(option.value) > -1"
          :class="{
            'selected': model.indexOf(option.value) > -1,
            disabled,
          }"
          :title="option.label ?? String(option.value)"
          type="button"
          @click="() => !disabled ? toggleBubble(option) : null"
        >
          {{ option.label }}
        </button>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  color: var(--colour-ti-base);
  font-family: 'Inter', 'sans-serif';
  font-size: var(--txt-input);
  line-height: var(--line-height-input);
  font-weight: 400;
}

.bubble-list {
  padding: 0;
  display: flex;
  justify-content: space-between;
  list-style: none;
}

.label {
  width: 100%;
  font-weight: 600;
}

.tbpro-bubble {
  transition: all 250ms ease-out;

  display: flex;
  justify-content: center;
  align-items: center;

  width: 2rem;
  height: 2rem;
  border: 0.0625rem solid var(--colour-neutral-border);
  border-radius: 100%;
  background-color: var(--colour-neutral-subtle);
  font-weight: 700;
  line-height: 150%;
  color: var(--colour-ti-muted);
}
.selected {
  background-color: var(--colour-service-primary);
  border-color: var(--colour-service-primary-pressed);
  color: var(--colour-neutral-base);
}
.required {
  color: var(--colour-ti-critical);
}
.disabled {
  cursor: default;
}
.selected.disabled {
  background-color: var(--colour-neutral-border);
  border-color: var(--colour-ti-muted);
  color: var(--colour-ti-muted);
}
</style>
