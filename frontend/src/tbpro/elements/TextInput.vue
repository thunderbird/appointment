<script setup lang="ts">
import { ref } from 'vue';
import { HTMLInputElementEvent } from '@/models';

const inputRef = ref<HTMLInputElement>(null);
/**
 * Forwards focus intent to the text input element.
 * Unlike HTMLElement.focus() this does not take any parameters.
 */
const focus = () => {
  if (!inputRef.value) {
    return;
  }
  inputRef.value.focus();
};

// component properties
interface Props {
  name: string;
  type?: string;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
};
withDefaults(defineProps<Props>(), {
  type: 'text',
  placeholder: '',
  required: false,
  disabled: false,
})

defineEmits(['submit']);
defineExpose({ focus });

const model = defineModel<string>();
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
      <span v-if="required && model?.length === 0" class="required">*</span>
    </span>
    <input
      v-model="model"
      :type="type"
      :id="name"
      :name="name"
      :disabled="disabled"
      :placeholder="placeholder"
      :required="required"
      @invalid="onInvalid"
      ref="inputRef"
    />
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

input {
  width: 100%;

  background-color: var(--tbpro-input);
  border-color: var(--tbpro-input-border);
  border-radius: var(--border-radius);

  &:hover:enabled {
    border-color: var(--tbpro-input-hover-border);
  }

  &:active:enabled {
    background-color: var(--tbpro-select-open);
    border-color: var(--tbpro-select-open-border);
  }

  &:focus:enabled {
    border-radius: 0.125rem;
  }

  &:invalid {
    border-color: var(--critical);
  }

  &:disabled {
    filter: grayscale(50%);
    cursor: not-allowed;
  }

  &::placeholder {
    color: var(--tbpro-text-muted);
  }
}
</style>
