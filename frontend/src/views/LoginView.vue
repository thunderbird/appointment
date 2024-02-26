<template>
  <!-- page title area -->
  <div class="flex-center flex h-screen w-full bg-gray-100 dark:bg-gray-600">
    <div class="my-auto flex w-1/2 max-w-lg flex-col items-center justify-center gap-2 bg-white px-4 py-12 shadow-lg dark:bg-gray-700">
      <img class="mb-2 w-full max-w-[8rem]" src="/appointment_logo.svg" alt="Appointment Logo" />
      <div class="text-center text-4xl font-light">{{ t('app.title') }}</div>
      <div
        class="my-8 grid w-full"
        :class="{'gap-8': isPasswordAuth, 'grid-rows-2': isPasswordAuth, 'gap-4': isFxaAuth}"
      >
        <label class="mt-4 flex items-center pl-4">
          <span class="w-full" :class="{'max-w-[4em]': isFxaAuth, 'max-w-[6rem]': isPasswordAuth}">
            {{ t('label.email') }}
          </span>
          <input
            v-model="username"
            type="email"
            class="mr-6 w-full rounded-md"
            :class="{'mr-4': isFxaAuth}"
            @keydown.enter="isFxaAuth ? login() : null"
          />
        </label>
        <div v-if="isFxaAuth" class="text-center text-sm">{{ t('text.login.continueToFxa') }}</div>
        <label v-if="isPasswordAuth" class="mt-4 flex items-center pl-4">
          <span class="w-full max-w-[6rem]">{{ t('label.password') }}</span>
          <input
            v-model="password"
            type="password"
            class="mr-6 w-full rounded-md"
            @keyup.enter="login"
          />
        </label>
      </div>
      <primary-button class="bottom-0" :label="isFxaAuth ? t('label.continue') : t('label.logIn')" @click="login"/>
    </div>
  </div>
</template>

<script setup>
import {
  inject, ref,
} from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user-store';
import PrimaryButton from '@/elements/PrimaryButton';

// component constants
const user = useUserStore();

// component constants
const { t } = useI18n();
const call = inject('call');
const dj = inject('dayjs');
const router = useRouter();
const isPasswordAuth = inject('isPasswordAuth');
const isFxaAuth = inject('isFxaAuth');

// list of pending appointments
const username = ref('');
const password = ref('');

// do log out
const login = async () => {
  if (!username.value) {
    return;
  }

  if (isFxaAuth) {
    const params = new URLSearchParams({
      email: username.value,
      timezone: dj.tz.guess(),
    });
    const { error, data } = await call(`fxa_login?${params}`).get().json();
    const { url } = data.value;

    if (error.value) {
      return;
    }

    window.location = url;
    return;
  }

  if (!password.value) {
    return;
  }

  await user.login(call, username.value, password.value);
  await router.push('/calendar');
};
</script>
