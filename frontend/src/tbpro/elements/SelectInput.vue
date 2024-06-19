<script setup>
import { ref } from 'vue';

defineProps({
  name: String,
  options: Object,
  required: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
});
defineEmits(['submit']);
const model = defineModel();
const isInvalid = ref(false);
const validationMessage = ref('');

const onInvalid = (evt) => {
  isInvalid.value = true;
  validationMessage.value = evt.target.validationMessage;
};
</script>

<template>
  <label class="wrapper" :for="name">
    <span class="label">
      <slot/>
      <span v-if="required && model.length === 0" class="required">*</span>
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
    <span v-if="isInvalid" class="flex w-full text-left text-rose-500">
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

.required {
  color: var(--critical);
}

select {
  background-color: var(--tbpro-input);
  border-color: var(--tbpro-input-border);
  border-radius: var(--border-radius);

  &:hover {
    border-color: var(--tbpro-input-hover-border);
  }

  &:active {
    background-color: var(--tbpro-select-open);
    border-color: var(--tbpro-select-open-border);
  }
}
</style>
