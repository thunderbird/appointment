<script setup lang="ts">
import { inject, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { createUserStore } from '@/stores/user-store';
import { LOGIN_REDIRECT_KEY } from '@/definitions';
import { callKey, isAccountsAuthKey } from '@/keys';

const route = useRoute();
const router = useRouter();

// component constants
const call = inject(callKey);
const user = createUserStore(call);

const isFxaAuth = computed(() => import.meta.env?.VITE_AUTH_SCHEME === 'fxa');
const isAccountsAuth = inject(isAccountsAuthKey);

onMounted(async () => {
  // Retrieve and remove temp login redirect location
  const redirectTo = window.sessionStorage?.getItem(LOGIN_REDIRECT_KEY);
  window.sessionStorage?.removeItem(LOGIN_REDIRECT_KEY);
  // Remove any ftue steps on new login
  window.localStorage?.removeItem('tba/ftue');

  if (!isFxaAuth.value && !isAccountsAuth) {
    await router.push(redirectTo ?? '/');
    return;
  }

  if (isAccountsAuth) {
    await user.login('true', null);
  } else {
    await user.login(route.params.token as string, null);
  }

  // If we don't have a redirectTo or it's to logout then push to dashboard!
  if (!redirectTo || redirectTo === '/logout') {
    await router.push('/dashboard');
    return;
  }

  await router.push(redirectTo);
});
</script>

<template>
  <div>
    <!-- Intentionally left blank -->
  </div>
</template>
