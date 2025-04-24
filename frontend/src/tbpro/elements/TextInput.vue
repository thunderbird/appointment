<script setup lang="ts">
import { ref, computed } from 'vue';
import { useElementSize } from '@vueuse/core';
import { HTMLInputElementEvent } from '@/models';

const model = defineModel<string>();
const isInvalid = ref(false);
const validationMessage = ref('');
const isDirty = ref(false);
const inputRef = ref<HTMLInputElement>(null);
const inputPrefix = ref<HTMLSpanElement>(null);
const { width: inputPrefixWidth } = useElementSize(inputPrefix); // Calculate the width of the prefix element

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
  error?: string;
  type?: string;
  placeholder?: string;
  prefix?: string; // A prefix shows up inside the input field and moves the actual editable area to the right.
  outerPrefix?: string; // A prefix shows up outside the input field and moves the whole input to the right.
  required?: boolean;
  disabled?: boolean;
  smallText?: boolean;
  maxLength?: number|string;
}
const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  help: null,
  error: null,
  placeholder: null,
  prefix: null,
  required: false,
  disabled: false,
  smallText: false,
  maxLength: null,
});

defineEmits(['submit']);
defineExpose({ focus });

// Calculate padding left for the actual input considering prefix width and existing padding
const inputPaddingLeft = computed(() => (props.prefix ? `${inputPrefixWidth.value + 12}px` : '12px'));

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
  inputRef.value.setCustomValidity('');
  isInvalid.value = false;
  isDirty.value = true;
  validationMessage.value = '';
};
</script>

<template>
  <label class="wrapper" :for="name">
    <span class="label">
      <slot/>
      <span v-if="required && $slots.default && model?.length === 0" class="required">*</span>
    </span>
    <span class="tbpro-input" :class="{'small-text': props.smallText}" >
      <span v-if="outerPrefix" class="tbpro-input-outer-prefix">{{ outerPrefix }}</span>
      <span class="tbpro-input-wrapper">
        <span v-if="prefix" ref="inputPrefix" class="tbpro-input-prefix">{{ prefix }}</span>
        <input
          class="tbpro-input-element"
          v-model="model"
          :class="{ 'dirty': isDirty }"
          :type="type"
          :id="name"
          :name="name"
          :disabled="disabled"
          :placeholder="placeholder"
          :required="required"
          :maxLength="maxLength"
          @invalid.prevent="onInvalid"
          @change="onChange"
          ref="inputRef"
          :style="{ paddingLeft: inputPaddingLeft }"
        />
      </span>
    </span>
    <span v-if="isInvalid" class="help-label invalid">
      {{ validationMessage }}
    </span>
    <span v-else-if="error" class="help-label invalid">
      {{ error }}
    </span>
    <span v-else-if="help" class="help-label">
      {{ help }}
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
  font-family: var(--font-sans);
  font-size: var(--txt-input);
  line-height: var(--line-height-input);
  font-weight: 400;
}

.label {
  width: 100%;
  font-weight: 500;
}

.small-text {
  --txt-input: 0.7384375rem;
}

.help-label {
  display: flex;
  color: var(--colour-ti-base);

  width: 100%;
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
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  width: 100%;

  .tbpro-input-outer-prefix {
    white-space: nowrap;
  }

  .tbpro-input-wrapper {
    position: relative;
    width: 100%;
  
    .tbpro-input-prefix {
      position: absolute;
      top: 0.70rem;
      left: 12px;
      font-size: var(--txt-input);
      line-height: var(--line-height-input);
      color: var(--colour-ti-muted);
      user-select: none;
      text-overflow: '.../';
      overflow: hidden;
      max-width: 40%;
      text-wrap: nowrap;
      z-index: 1;
    }
  
    .tbpro-input-element {
      --colour-btn-border: var(--colour-neutral-border);
      width: 100%;
      transition-property: none;
      font-size: var(--txt-input);
  
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
  
      &[type="time"]::-webkit-calendar-picker-indicator {
        margin-right: -0.5rem;
        background: none;
      }
    }
  }
}
.dark {
  .tbpro-input-element {
    background-color: var(--colour-neutral-lower);
  }
}
</style>
