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
      class="tbpro-select w-full rounded-md"
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
  visibility: hidden;
  display: flex;
  color: var(--colour-ti-critical);

  width: 100%;
  min-height: 0.9375rem;
  font-size: 0.625rem;
  line-height: 0.9375rem;
}

.visible {
  visibility: visible;
}

.required {
  color: var(--colour-ti-critical);
}

.tbpro-select {
  --colour-select-border: var(--colour-neutral-border);
  background-color: var(--colour-neutral-base);
  @mixin faded-border var(--colour-select-border);
  border-radius: var(--border-radius);
  font-weight: 400;


  &:hover, &:focus {
    --colour-select-border: var(--colour-neutral-border-intense);
  }

  &:active {
    background-color: var(--colour-neutral-subtle);
    --colour-select-border: var(--colour-neutral-border-intense);
  }
}
.dark {
  .tbpro-select {
    background-color: var(--colour-neutral-lower);
  }
}
</style>
