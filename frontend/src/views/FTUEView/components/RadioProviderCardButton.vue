<script setup lang="ts">
import { computed } from 'vue';
import ProviderCardButton from './ProviderCardButton.vue';

const props = defineProps<{
  title: string;
  description: string;
  iconSrc: string;
  iconAlt: string;
  value: string;
  modelValue?: string;
  name: string;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: string];
}>();

const isSelected = computed(() => props.modelValue === props.value);

const handleClick = () => {
  emit('update:modelValue', props.value);
};

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    handleClick();
  }
};
</script>

<template>
  <label
    :class="{ selected: isSelected }"
    @click="handleClick"
    @keydown="handleKeydown"
    role="radio"
    :aria-checked="isSelected"
    :aria-label="title"
    :tabindex="0"
  >
    <input
      type="radio"
      :name="name"
      :value="value"
      :checked="isSelected"
      @change="handleClick"
      tabindex="-1"
      aria-hidden="true"
    />
    <provider-card-button
      :title="title"
      :description="description"
      :iconSrc="iconSrc"
      :iconAlt="iconAlt"
      tabindex="-1"
    />
  </label>
</template>

<style scoped>
label {
  display: block;
  cursor: pointer;
  border: 2px solid transparent;
  border-radius: 0.5rem;
  outline: none;

  &:focus-visible {
    outline: 2px solid var(--colour-ti-highlight);
    outline-offset: 2px;
  }

  &.selected {
    border-color: color-mix(in srgb, var(--colour-ti-highlight) 30%, transparent);
  }
}

input[type="radio"] {
  position: absolute;
  opacity: 0;
  pointer-events: none;
  width: 0;
  height: 0;
}

/* Prevent the inner button from interfering with label clicks */
label :deep(button) {
  pointer-events: none;
  cursor: inherit;
}

@media (prefers-reduced-motion: no-preference) {
  label {
    transition: border-color 0.2s;
  }
}
</style>
