<script setup lang="ts">
import { ref } from 'vue';
import { HTMLInputElementEvent } from '@/models';

const model = defineModel<string>();
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

// component properties
interface Props {
  name: string;
  help?: string;
  remoteError?: string;
  type?: string;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
}
withDefaults(defineProps<Props>(), {
  type: 'text',
  help: null,
  remoteError: null,
  placeholder: '',
  required: false,
  disabled: false,
});

defineEmits(['submit']);
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
};
</script>

<template>
  <label class="wrapper" :for="name">
    <span class="label">
      <slot/>
      <span v-if="required && model?.length === 0" class="required">*</span>
    </span>
    <input
      class="tbpro-input"
      v-model="model"
      :class="{'dirty': isDirty}"
      :type="type"
      :id="name"
      :name="name"
      :disabled="disabled"
      :placeholder="placeholder"
      :required="required"
      @invalid="onInvalid"
      @change="onChange"
      ref="inputRef"
    />
    <span v-if="isInvalid" class="help-label invalid">
      {{ validationMessage }}
    </span>
    <span v-else-if="help" class="help-label">
      {{ help }}
    </span>
    <span v-else class="help-label">
      <!-- Empty space -->
    </span>
  </label>
</template>

<style scoped>
@import '@/assets/styles/mixins.pcss';

.wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: var(--colour-ti-base);
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

.tbpro-input {
  --colour-btn-border: var(--colour-neutral-border);
  width: 100%;

  background-color: var(--colour-neutral-base);
  border-radius: var(--border-radius);
  @mixin faded-border var(--colour-btn-border);

  &:hover:enabled {
    --colour-btn-border: var(--colour-neutral-border-intense);
  }

  &:active:enabled {
    --colour-btn-border: var(--colour-neutral-border-intense);
  }

  &:focus:enabled {
    border-radius: 0.125rem;
  }

  &.dirty:invalid {
    --colour-btn-border: var(--colour-ti-critical);
  }

  &:disabled {
    filter: grayscale(50%);
    cursor: not-allowed;
  }

  &::placeholder {
    color: var(--colour-ti-muted);
  }
}
.dark {
  .tbpro-input {
    background-color: var(--colour-neutral-lower);
  }
}
</style>
