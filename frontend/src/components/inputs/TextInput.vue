<script setup>
import { ref } from 'vue';

defineProps({
  name: String,
  placeholder: {
    type: String,
    default: '',
  },
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
    <input
      v-model="model"
      type="text"
      class="w-full rounded-md"
      :class="{'!border-rose-500': isInvalid}"
      :id="name"
      :name="name"
      :disabled="disabled"
      :placeholder="placeholder"
      :required="required"
      @invalid="onInvalid"
    />
    <span v-if="isInvalid" class="apmt-error-color flex w-full text-left">
      {{ validationMessage }}
    </span>
  </label>
</template>

<style scoped>
</style>
