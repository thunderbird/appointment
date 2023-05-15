<template>
<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert" :class="{hidden: isHidden}">
  <strong class="font-bold">{{ title }}:</strong>
  <span class="block sm:inline ml-1"><slot></slot></span>
  <span class="absolute top-0 bottom-0 right-0 px-4 py-3" @click="onClose">
    <icon-x class="h-6 w-6 stroke-1 fill-transparent stroke-red-500 cursor-pointer" />
  </span>
</div>
</template>

<script setup>
import { ref } from 'vue';
import { IconX } from '@tabler/icons-vue';

defineProps({
  title: String,
});

const isHidden = ref(false);
const onClose = () => { isHidden.value = true; };
</script>
