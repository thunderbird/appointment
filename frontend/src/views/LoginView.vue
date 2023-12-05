<template>
  <!-- page title area -->
  <div class="flex flex-col gap-2 justify-center items-center">
    <img class="w-full max-w-[8rem] mb-2" src="/appointment_logo.svg" alt="Appointment Logo" />
    <div class="text-4xl font-light">Login to Continue</div>
    <div class="grid mt-8 mb-12 gap-8 max-w-lg w-full" :class="{'grid-rows-2': isPasswordAuth}">
      <label class="pl-4 mt-4 flex items-center">
        <span class="w-full max-w-[6rem]">{{ isFxaAuth ? 'Email' : 'Username' }}</span>
        <input
          v-model="username"
          type="text"
          class="w-full rounded-md"
        />
      </label>
      <label v-if="isPasswordAuth" class="pl-4 mt-4 flex items-center">
        <span class="w-full max-w-[6rem]">Password</span>
        <input
          v-model="password"
          type="text"
          class="w-full rounded-md"
        />
      </label>
    </div>
    <primary-button :label="t('label.logIn')" @click="login()"/>
  </div>
</template>

<script setup>
import {
  inject, computed, ref,
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
const router = useRouter();

// list of pending appointments
const username = ref('melissa@thunderbird.net');
const password = ref('test');

const isPasswordAuth = computed(() => process.env?.VUE_APP_AUTH_SCHEME === 'password');
const isFxaAuth = computed(() => process.env?.VUE_APP_AUTH_SCHEME === 'fxa');

// do log out
const login = async () => {
  if (isFxaAuth.value) {
    const { error, data } = await call(`fxa_login?email=${username.value}`).get().json();
    const { url } = data.value;

    if (error.value) {
      return;
    }

    window.location = url;
    return;
  }

  await user.login(call, username.value, password.value);
  await router.push('/calendar');
};
</script>
