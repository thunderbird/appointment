<script setup>
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
</script>

<template>
  <label class="flex flex-col items-center pl-4" :for="name">
    <span class="flex w-full justify-between">
      <slot/>
      <span v-if="required" class="content-center pr-4 text-red-500">*</span>
    </span>
    <input
      v-model="model"
      type="text"
      class="mr-6 w-full rounded-md"
      :id="name"
      :name="name"
      :disabled="disabled"
      :placeholder="placeholder"
      :required="required"
    />
  </label>
</template>

<style scoped>

</style>
