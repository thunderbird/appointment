<script setup lang="ts">
import { SelectOption } from "@/models";

// component properties
interface Props {
  options: SelectOption[];
};
defineProps<Props>();

const model = defineModel<number[]>({ default: [] });

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
  <ul>
    <li v-for="option in options" :key="option.value">
      <button
        :class="{'selected': model.indexOf(option.value) > -1}"
        type="button"
        @click="() => toggleBubble(option)"
      >
        {{ option.label }}
      </button>
    </li>
  </ul>
</template>

<style scoped>
ul {
  display: flex;
  gap: 0.625rem;
  list-style: none;
}

button {
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
</style>
