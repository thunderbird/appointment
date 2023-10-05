<template>
  <div class="h-full p-4 flex-center flex-col gap-8 select-none">
    <img class="w-full max-w-md" src="/appointment_logo.svg" alt="Appointment Logo" />
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
