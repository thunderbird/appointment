<script setup lang="ts">
import { ref } from 'vue';
import { HTMLInputElementEvent } from '@/models';

// component properties
interface Props {
  name: string;
  label?: string;
  help?: string;
  error?: string;
  checked?: boolean;
  required?: boolean;
  disabled?: boolean;
}
withDefaults(defineProps<Props>(), {
  label: null,
  help: null,
  error: null,
  checked: false,
  required: false,
  disabled: false,
});

const model = defineModel<boolean>();
const isInvalid = ref(false);
const validationMessage = ref('');
const isDirty = ref(false);
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

const emit = defineEmits(['submit', 'change']);
defineExpose({ focus });

const onInvalid = (evt: HTMLInputElementEvent) => {
  isInvalid.value = true;
  isDirty.value = true;
  validationMessage.value = evt.target.validationMessage;
};
/**
 * On any change we mark the element as dirty
 * this is so we can delay :invalid until
 * the user does something worth invalidating
 */
const onChange = () => {
  isDirty.value = true;
  emit('change');
};
</script>

<template>
  <div class="checkbox-input-wrapper">
    <label class="checkbox-input-label" :for="name">
      <input
        class="checkbox-input"
        v-model="model"
        type="checkbox"
        :class="{ 'dirty': isDirty }"
        :id="name"
        :name="name"
        :checked="checked"
        :disabled="disabled"
        :required="required"
        @invalid="onInvalid"
        @change="onChange"
        ref="inputRef"
      />
      <span v-if="label">{{ label }}</span>
      <span v-if="required" class="required">*</span>
    </label>
    <span v-if="isInvalid" class="help-label invalid">
      {{ validationMessage }}
    </span>
    <span v-else-if="error" class="help-label invalid">
      {{ error }}
    </span>
    <span v-else-if="help" class="help-label">
      {{ help }}
    </span>
  </div>
</template>

<style scoped>
.checkbox-input-wrapper {
  --colour-highlight: var(--colour-service-primary);
  display: flex;
  flex-direction: column;
  align-items: start;
  color: var(--colour-ti-base);
  font-family: var(--font-sans);
  font-size: var(--txt-input);
  line-height: var(--line-height-input);
  font-weight: 400;
  width: 100%;
}
.dark {
  .checkbox-input-wrapper {
    --colour-highlight: var(--colour-service-secondary);
  }
}

.checkbox-input-label {
  display: flex;
  gap: 0.625rem;
  justify-content: flex-start;
  align-items: center;
  font-weight: 500;
}

.help-label {
  display: flex;
  color: var(--colour-ti-base);

  width: 100%;
  min-height: 0.9375rem;
  font-size: 0.625rem;
  line-height: 0.9375rem;
  padding: 0.1875rem;

  &.invalid {
    color: var(--colour-danger-default);
  }
}

.required {
  color: var(--colour-ti-critical);
}

.checkbox-input {
  width: 1.0rem;
  height: 1.0rem;
  border-radius: var(--border-radius);
  border: 1px solid var(--colour-neutral-border-intense);

  &:focus {
    outline-color: var(--colour-highlight);
  }

  &:checked, &:checked:hover, &:checked:focus {
    background-color: var(--colour-highlight);
    border-color: var(--colour-highlight);
    color: var(--colour-neutral-raised);
  }

  &:disabled {
    cursor: not-allowed;
  }
}
</style>
