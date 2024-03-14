<template>
  <div>
    <!-- Intentionally left blank -->
  </div>
</template>

<script setup>
import { inject, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user-store';
import { loginRedirectKey } from '@/definitions';

const route = useRoute();
const router = useRouter();

// component constants
const user = useUserStore();

// component constants
const call = inject('call');

const isFxaAuth = computed(() => import.meta.env?.VITE_AUTH_SCHEME === 'fxa');

onMounted(async () => {
  // Retrieve and remove temp login redirect location
  const redirectTo = window.sessionStorage?.getItem(loginRedirectKey);
  window.sessionStorage?.removeItem(loginRedirectKey);

  if (!isFxaAuth.value) {
    await router.push(redirectTo ?? '/');
    return;
  }

  await user.login(call, route.params.token, null);
  await router.push(redirectTo ?? '/calendar');
});
</script>
