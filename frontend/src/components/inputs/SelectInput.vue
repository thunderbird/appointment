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
  <label class="flex flex-col items-center" :for="name">
    <span class="ml-6 flex w-full justify-between">
      <slot/>
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

</style>
