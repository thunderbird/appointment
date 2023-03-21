<template>
  <div class="h-full p-4 flex-center flex-col gap-8 select-none">
    TODO: Some great introduction visuals and text to make user click the sign up button.
  </div>
</template>

<script setup>
import { inject, onMounted } from 'vue';

const refresh = inject('refresh');

// initially load data when component gets remounted
onMounted(async () => {
  await refresh();
});
</script>
