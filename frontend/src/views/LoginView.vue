<template>
  <!-- page title area -->
  <div class="flex-center runded flex h-screen w-full bg-gray-100 dark:bg-gray-600">
    <div class="my-auto flex w-full flex-col items-center justify-center gap-2 rounded-md bg-white px-4 py-12 shadow-lg dark:bg-gray-700 md:w-1/2 md:max-w-lg">
      <img class="mb-2 w-full max-w-32" src="/appointment_logo.svg" alt="Appointment Logo"/>
      <div class="text-center text-4xl font-light">{{ t('app.title') }}</div>
      <alert-box v-if="loginError" @close="closeError" class="mt-4">
        {{ loginError }}
      </alert-box>
      <div class="flex w-full flex-col items-center justify-center px-4" v-if="showConfirmEmailScreen">
        <div class="my-8 grid w-full gap-8">
          <h2 class="text-xl">{{ t('waitingList.signUpHeading') }}</h2>
          <p>{{ t('waitingList.signUpInfo') }}</p>
          <p>{{ t('waitingList.signUpCheckYourEmail') }}</p>
        </div>
        <primary-button
          :label="t('label.back')"
          class="btn-back"
          @click="goHome"
          :title="t('label.back')"
          :disabled="isLoading"
        />
      </div>
      <div class="flex w-full flex-col items-center justify-center px-4" v-else>
        <div class="my-8 grid w-full gap-8">
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
          <label class="flex flex-col items-center pl-4" v-if="showInviteFlow">
          <span class="w-full">
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
          v-if="showInviteFlow && inviteCode.length > 0"
          :label="t('label.signUpWithInviteCode')"
          class="btn-login-with-invite-code"
          @click="login"
          :title="t('label.signUpWithInviteCode')"
          :disabled="isLoading"
        />
        <primary-button
          v-else-if="showInviteFlow"
          :label="t('label.addToWaitingList')"
          class="btn-add-to-waiting-list"
          @click="signUp"
          :title="t('label.addToWaitingList')"
          :disabled="isLoading"
        />
        <primary-button
          v-else-if="!isFxaAuth"
          :label="t('label.logIn')"
          class="btn-login"
          @click="login"
          :title="t('label.logIn')"
          :disabled="isLoading"
        />
        <primary-button
          v-else
          :label="t('label.continue')"
          class="btn-continue"
          @click="login"
          :title="t('label.continue')"
          :disabled="isLoading"
        />
      </div>
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
const showInviteFlow = ref(false);
const isLoading = ref(false);

// form input and error
const username = ref('');
const password = ref('');
const loginError = ref(null);
const inviteCode = ref('');
const showConfirmEmailScreen = ref(false);

const closeError = () => {
  loginError.value = null;
};

const goHome = () => {
  router.push('/');
};

const signUp = async () => {
  isLoading.value = true;
  loginError.value = '';
  const { data } = await call('/waiting-list/join').post({
    email: username.value,
  }).json();

  if (!data.value) {
    loginError.value = t('waitingList.signUpAlreadyExists');
  } else {
    showConfirmEmailScreen.value = true;
  }

  isLoading.value = false;
};

const login = async () => {
  if (!username.value || (isPasswordAuth && !password.value)) {
    loginError.value = t('error.credentialsIncomplete');
    return;
  }

  isLoading.value = true;

  // If they come here the first time we check if they're allowed to login
  // If they come here a second time after not being allowed it's because they have an invite code.
  if (!showInviteFlow.value) {
    const { data: canLogin, error } = await call('/can-login').post({
      email: username.value,
    }).json();

    if (error?.value) {
      // Bleh
      loginError.value = canLogin?.value?.detail[0]?.msg;
      isLoading.value = false;
      return;
    }

    if (!canLogin.value) {
      showInviteFlow.value = true;
      isLoading.value = false;
      return;
    }
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
      isLoading.value = false;
      return;
    }

    window.location = url;
    return;
  }

  const { error } = await user.login(call, username.value, password.value);
  if (error) {
    loginError.value = error;
    isLoading.value = false;
    return;
  }

  await router.push('/calendar');
};
</script>
