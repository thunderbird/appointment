<template>
  <label class="relative flex justify-between items-center w-full">
    {{ label }}
    <input type="checkbox" class="hidden peer" :checked="active" />
    <div class="w-10 h-5 flex items-center flex-shrink-0 ml-4 py-1 bg-gray-300 rounded-full duration-300 ease-in-out peer-checked:after:bg-teal-500 after:w-5 after:h-5 after:bg-gray-400 after:rounded-full after:shadow-md after:duration-300 peer-checked:after:translate-x-5"></div>
  </label>
</template>

<script setup>
// component properties
defineProps({
  active: Boolean, // toggle state
  label: String    // input label
});
</script>
