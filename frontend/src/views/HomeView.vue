<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user-store';

const router = useRouter();
const user = useUserStore();

onMounted(() => {
  if (user.authenticated) {
    router.push('/dashboard');
  } else {
    router.push('/login');
  }
});
</script>

<template>
  <div />
</template>
