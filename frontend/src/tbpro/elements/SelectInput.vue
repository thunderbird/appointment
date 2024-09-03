<script setup lang="ts">
import { ref } from 'vue';
import { HTMLInputElementEvent, SelectOption } from '@/models';

// component properties
interface Props {
  name: string;
  options: SelectOption[];
  required?: boolean;
  disabled?: boolean;
};
withDefaults(defineProps<Props>(), {
  required: false,
  disabled: false,
})

defineEmits(['submit']);
const model = defineModel<number|string>();
const isInvalid = ref(false);
const validationMessage = ref('');

const onInvalid = (evt: HTMLInputElementEvent) => {
  isInvalid.value = true;
  validationMessage.value = evt.target.validationMessage;
};
</script>

<template>
  <label class="wrapper" :for="name">
    <span class="label">
      <slot/>
      <span v-if="required && (model === null || model === '')" class="required">*</span>
    </span>
    <select
      class="w-full rounded-md"
      v-model="model"
      :id="name"
      :name="name"
      :required="required"
      :disabled="disabled"
      @invalid="onInvalid"
    >
      <option v-for="option in options" :value="option.value" :key="option.value">
        {{ option.label }}
      </option>
    </select>
    <span :class="{'visible': isInvalid}" class="help-label">
      {{ validationMessage }}
    </span>
  </label>
</template>

<style scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: var(--tbpro-text);
  font-family: 'Inter', 'sans-serif';
  font-size: var(--txt-input);
  line-height: var(--line-height-input);
  font-weight: 400;
}

.label {
  width: 100%;
  font-weight: 600;
}

.help-label {
  visibility: hidden;
  display: flex;
  color: var(--critical-default);

  width: 100%;
  min-height: 0.9375rem;
  font-size: 0.625rem;
  line-height: 0.9375rem;
}

.visible {
  visibility: visible;
}

.required {
  color: var(--critical);
}

select {
  background-color: var(--tbpro-input);
  border-color: var(--tbpro-input-border);
  border-radius: var(--border-radius);

  font-weight: 400;

  &:hover {
    border-color: var(--tbpro-input-hover-border);
  }

  &:active {
    background-color: var(--tbpro-select-open);
    border-color: var(--tbpro-select-open-border);
  }
}
</style>
