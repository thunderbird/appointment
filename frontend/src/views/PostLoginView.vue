<template>
  <div>
    <!-- Intentionally left blank -->
  </div>
</template>

<script setup>
import {
  inject, computed, onMounted,
} from 'vue';
import { useUserStore } from '@/stores/user-store';
import {useRoute, useRouter} from 'vue-router';

const route = useRoute();
const router = useRouter();

// component constants
const user = useUserStore();

// component constants
const call = inject('call');

const isFxaAuth = computed(() => process.env?.VUE_APP_AUTH_SCHEME === 'fxa');

onMounted(async () => {
  if (!isFxaAuth.value) {
    await router.push('/');
    return;
  }

  await user.login(call, route.params.token, null);
  await router.push('/calendar');
});
</script>
