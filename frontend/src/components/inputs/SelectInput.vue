<script setup>
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
</script>

<template>
  <label class="flex flex-col items-center pl-4" :for="name">
    <span class="flex w-full justify-between">
      <slot/>
      <span v-if="required" class="content-center pr-4 text-red-500">*</span>
    </span>
    <select
      class="mr-6 w-full rounded-md"
      v-model="model"
      :id="name"
      :name="name"
      :required="required"
      :disabled="disabled"
    >
      <option v-for="option in options" :value="option.value" :key="option.value">
        {{ option.label }}
      </option>
    </select>
  </label>
</template>

<style scoped>

</style>
