<template>
  <!-- page title area -->
  <div class="flex flex-col gap-2 justify-center items-center">
    <div class="text-4xl font-light">Login</div>
    <div class="grid grid-cols-2 mt-8 mb-12 gap-8">
      <label class="pl-4 mt-4 flex items-center">
        <div class="w-full max-w-2xs">Username</div>
        <input
          v-model="username"
          type="text"
          class="w-full rounded-md"
        />
      </label>
      <label v-if="isPasswordAuth" class="pl-4 mt-4 flex items-center">
        <div class="w-full max-w-2xs">Password</div>
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
import {inject, computed, onMounted, ref} from 'vue';
import {useI18n} from 'vue-i18n';
import {useUserStore} from '@/stores/user-store';
import PrimaryButton from '@/elements/PrimaryButton';

// component constants
const user = useUserStore();

// component constants
const {t} = useI18n();
const call = inject('call');


// list of pending appointments
const username = ref('melissa@thunderbird.net');
const password = ref('test');

const isPasswordAuth = computed(() => process.env?.VUE_APP_AUTH_SCHEME === 'password');
const isFxaAuth = computed(() => process.env?.VUE_APP_AUTH_SCHEME === 'fxa');

// do log out
const login = async () => {
  user.reset();
  await user.login(call, username.value, password.value);
};
</script>
