<script setup lang="ts">
import { SelectOption } from '@/models';

const props = defineProps<{
  legend: string;
  name: string;
  disabled?: boolean;
  options: SelectOption<string | number>[];
}>()

const model = defineModel<string | number>();
</script>

<template>
  <fieldset>
    <legend>{{ props.legend }}:</legend>

    <div class="pill-container">
      <div
        v-for="option in props.options"
        :key="option.value"
        class="pill-item"
      >
        <input
          type="radio"
          :id="`${props.name}-${option.value}`"
          :name="props.name"
          :value="option.value"
          :class="{ 'screen-reader-only': model !== option.value }"
          :disabled="disabled"
          v-model="model"
        />
        <label :for="`${props.name}-${option.value}`">
          {{ option.label }}
        </label>
      </div>
    </div>
  </fieldset>
</template>

<style scoped>
legend {
  margin-block-end: 0.25rem;
  font-size: 0.725rem;
  font-weight: bold;
}

.pill-container {
  display: inline-flex;
  overflow: hidden;
  border: 1px solid var(--colour-apmt-primary);
  border-radius: 999px;

  &:has(input[type="radio"]:disabled) {
    border: 1px solid var(--colour-ti-muted);
  }
}

.pill-item {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.5rem;
  cursor: pointer;

  input[type="radio"] {
    transition: none;
    color: var(--colour-apmt-soft);
    width: 0.5rem;
    height: 0.5rem;
  }

  label {
    font-size: 0.75rem;
    cursor: pointer;
    text-transform: capitalize;
  }

  &:not(:last-child) {
    border-inline-end: 1px solid var(--colour-apmt-primary);

    &:has(input[type="radio"]:disabled) {
      border-inline-end: 1px solid var(--colour-ti-muted);
    }
  }

  &:has(input[type="radio"]:checked) {
    background-color: var(--colour-apmt-primary);
    color: var(--colour-neutral-base);
  }

  &:has(input[type="radio"]:checked)&:has(input[type="radio"]:disabled) {
    background-color: var(--colour-ti-muted);
    color: var(--colour-neutral-base);
  }
}
</style>