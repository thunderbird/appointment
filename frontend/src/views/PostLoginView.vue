<script setup lang="ts">
import { inject, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user-store';
import { loginRedirectKey } from '@/definitions';
import { callKey } from '@/keys';

const route = useRoute();
const router = useRouter();

// component constants
const user = useUserStore();

// component constants
const call = inject(callKey);

const isFxaAuth = computed(() => import.meta.env?.VITE_AUTH_SCHEME === 'fxa');

onMounted(async () => {
  // Retrieve and remove temp login redirect location
  const redirectTo = window.sessionStorage?.getItem(loginRedirectKey);
  window.sessionStorage?.removeItem(loginRedirectKey);
  // Remove any ftue steps on new login
  window.localStorage?.removeItem('tba/ftue');

  if (!isFxaAuth.value) {
    await router.push(redirectTo ?? '/');
    return;
  }

  await user.login(call, route.params.token as string, null);
  await router.push(redirectTo ?? '/calendar');
});
</script>

<template>
  <div>
    <!-- Intentionally left blank -->
  </div>
</template>
