<template>
  <!-- page title area -->
  <div class="flex-center flex h-screen w-full bg-gray-100 dark:bg-gray-600">
    <div class="my-auto flex w-full flex-col items-center justify-center gap-2 bg-white px-4 py-12 shadow-lg dark:bg-gray-700 md:w-1/2 md:max-w-lg">
      <img class="mb-2 w-full max-w-32" src="/appointment_logo.svg" alt="Appointment Logo" />
      <div class="text-center text-4xl font-light">{{ t('app.title') }}</div>
      <alert-box v-if="loginError" @close="loginError = null" class="mt-4">
        {{ loginError }}
      </alert-box>
      <div
        class="my-8 grid w-full gap-8"
      >
        <label class="flex flex-col items-center pl-4">
          <span class="w-full">
            {{ isPasswordAuth ? t('label.username') : t('label.email') }}
          </span>
          <input
            v-model="username"
            type="email"
            class="mr-6 w-full rounded-md"
            :class="{'mr-4': isFxaAuth}"
            @keydown.enter="isFxaAuth ? login() : null"
          />
        </label>
        <label class="flex flex-col items-center pl-4">
          <span class="w-full" >
          {{ t('label.inviteCode') }}
          </span>
          <input
            v-model="inviteCode"
            type="text"
            class="mr-6 w-full rounded-md"
            :class="{'mr-4': isFxaAuth}"
            @keydown.enter="isFxaAuth ? login() : null"
          />
        </label>
        <div v-if="isFxaAuth" class="text-center text-sm">{{ t('text.login.continueToFxa') }}</div>
        <label v-if="isPasswordAuth" class="flex flex-col items-center pl-4">
          <span class="w-full">{{ t('label.password') }}</span>
          <input
            v-model="password"
            type="password"
            class="mr-6 w-full rounded-md"
            @keyup.enter="login"
          />
        </label>
      </div>
      <primary-button
        v-if="!isFxaAuth"
        :label="$t('label.logIn')"
        class="btn-login"
        @click="login"
        :title="$t('label.logIn')"
      />
      <primary-button
        v-else
        :label="$t('label.continue')"
        class="btn-continue"
        @click="login"
        :title="$t('label.continue')"
      />
    </div>
  </div>
</template>

<script setup>
import { inject, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user-store';
import PrimaryButton from '@/elements/PrimaryButton';
import AlertBox from '@/elements/AlertBox';

// component constants
const user = useUserStore();

// component constants
const { t } = useI18n();
const call = inject('call');
const dj = inject('dayjs');
const router = useRouter();
const isPasswordAuth = inject('isPasswordAuth');
const isFxaAuth = inject('isFxaAuth');

// form input and error
const username = ref('');
const password = ref('');
const loginError = ref(null);
const inviteCode = ref('');

// do log out
const login = async () => {
  if (!username.value || (isPasswordAuth && !password.value)) {
    loginError.value = t('error.credentialsIncomplete');
    return;
  }

  if (isFxaAuth) {
    const params = new URLSearchParams({
      email: username.value,
      timezone: dj.tz.guess(),
    });

    if (inviteCode.value) {
      params.append('invite_code', inviteCode.value);
    }

    const { error, data } = await call(`fxa_login?${params}`).get().json();
    const { url } = data.value;

    if (error.value) {
      loginError.value = data.value?.detail;
      return;
    }

    window.location = url;
    return;
  }

  const { error } = await user.login(call, username.value, password.value);
  if (error) {
    loginError.value = error;
    return;
  }

  await router.push('/calendar');
};
</script>
