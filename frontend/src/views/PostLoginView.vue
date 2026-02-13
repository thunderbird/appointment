<script setup lang="ts">
import { inject, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { createUserStore } from '@/stores/user-store';
import { createExternalConnectionsStore } from '@/stores/external-connections-store';
import { INVITE_CODE_KEY, LOGIN_REDIRECT_KEY } from '@/definitions';
import { callKey, dayjsKey } from '@/keys';
import { userManager } from "@/composables/oidcUserManager";
import { BooleanResponse } from "@/models";
import { isFxaAuth, isOidcAuth } from "@/composables/authSchemes";

const route = useRoute();
const router = useRouter();

// component constants
const call = inject(callKey);
const user = createUserStore(call);
const externalConnectionsStore = createExternalConnectionsStore(call);
const dj = inject(dayjsKey);

onMounted(async () => {
  // Retrieve and remove temp login redirect location
  const redirectTo = window.sessionStorage?.getItem(LOGIN_REDIRECT_KEY);
  window.sessionStorage?.removeItem(LOGIN_REDIRECT_KEY);
  // Remove any ftue steps on new login
  window.localStorage?.removeItem('tba/ftue');

  const inviteCode = window.sessionStorage?.getItem(INVITE_CODE_KEY);
  window.sessionStorage?.removeItem(INVITE_CODE_KEY);

  if (isOidcAuth) {
    // Stored in an internal store
    const userData = await userManager.signinCallback(window.location.href);
    const { error, data }: BooleanResponse = await call('oidc/token').post({
      'access_token': userData.access_token,
      'invite_code': inviteCode,
      'timezone': dj.tz.guess(),
    }).json();

    if (error.value) {
      console.error("Err", data.value);
      return;
    }
  } else if (!isFxaAuth) {
    await router.push(redirectTo ?? '/');
    return;
  }

  if (isOidcAuth) {
    await user.login('true', null);
  } else {
    await user.login(route.params.token as string, null);
  }

  // Run health checks on external connections in the background
  externalConnectionsStore.checkStatus();

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
