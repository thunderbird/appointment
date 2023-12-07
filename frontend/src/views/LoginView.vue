<template>
  <!-- page title area -->
  <div class="flex w-full h-screen flex-center bg-gray-100 dark:bg-gray-600">
    <div class="flex flex-col gap-2 justify-center items-center shadow-lg px-4 py-12 my-auto w-1/2 max-w-lg bg-white dark:bg-gray-700">
      <img class="w-full max-w-[8rem] mb-2" src="/appointment_logo.svg" alt="Appointment Logo" />
      <div class="text-4xl font-light text-center">{{ t('app.title') }}</div>
      <div class="grid my-8 w-full" :class="{'gap-8': isPasswordAuth, 'grid-rows-2': isPasswordAuth, 'gap-4': isFxaAuth}">
        <label class="pl-4 mt-4 flex items-center">
          <span class="w-full" :class="{'max-w-[4em]': isFxaAuth, 'max-w-[6rem]': isPasswordAuth}">{{ t('label.email') }}</span>
          <input
            v-model="username"
            type="email"
            class="w-full rounded-md mr-6"
            :class="{'mr-4': isFxaAuth}"
            @keydown.enter="isFxaAuth ? login() : null"
          />
        </label>
        <div v-if="isFxaAuth" class="text-sm text-center">{{ t('text.login.continueToFxa') }}</div>
        <label v-if="isPasswordAuth" class="pl-4 mt-4 flex items-center">
          <span class="w-full max-w-[6rem]">{{ t('label.password') }}</span>
          <input
            v-model="password"
            type="password"
            class="w-full rounded-md mr-6"
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
const dj = inject("dayjs");
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
    const { error, data } = await call(`fxa_login?email=${username.value}&timezone=${dj.tz.guess()}`).get().json();
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
