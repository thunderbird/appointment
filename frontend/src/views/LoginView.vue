<script setup lang="ts">
import {inject, onMounted, ref} from 'vue';
import { useI18n } from 'vue-i18n';
import {useRoute, useRouter} from 'vue-router';
import { useUserStore } from '@/stores/user-store';
import { dayjsKey, callKey, isPasswordAuthKey, isFxaAuthKey } from "@/keys";
import { BooleanResponse, AuthUrlResponse, Exception, AuthUrl, Error } from "@/models";
import PrimaryButton from '@/elements/PrimaryButton.vue';
import AlertBox from '@/elements/AlertBox.vue';

// component constants
const user = useUserStore();

// component constants
const { t } = useI18n();
const call = inject(callKey);
const dj = inject(dayjsKey);
const route = useRoute();
const router = useRouter();
const isPasswordAuth = inject(isPasswordAuthKey);
const isFxaAuth = inject(isFxaAuthKey);
const onlyShowInvite = ref(false);
const showInviteFlow = ref(false);
const isLoading = ref(false);

// form input and error
const email = ref('');
const password = ref('');
const loginError = ref<string>(null);
const inviteCode = ref('');
const showConfirmEmailScreen = ref(false);

onMounted(() => {
  if (route.name === 'join-the-waiting-list') {
    showInviteFlow.value = true;
    onlyShowInvite.value = true;
  }
});

const closeError = () => {
  loginError.value = null;
};

const goHome = () => {
  router.push('/');
};

const signUp = async () => {
  isLoading.value = true;
  loginError.value = '';
  const { data }: BooleanResponse = await call('waiting-list/join').post({
    email: email.value,
  }).json();

  if (!data.value) {
    loginError.value = t('waitingList.signUpAlreadyExists');
  } else {
    showConfirmEmailScreen.value = true;
  }

  isLoading.value = false;
};

const login = async () => {
  if (!email.value || (isPasswordAuth && !password.value)) {
    loginError.value = t('error.credentialsIncomplete');
    return;
  }

  isLoading.value = true;

  // If they come here the first time we check if they're allowed to login
  // If they come here a second time after not being allowed it's because they have an invite code.
  if (!showInviteFlow.value) {
    const { data: canLogin, error }: BooleanResponse = await call('can-login').post({
      email: email.value,
    }).json();

    if (error?.value) {
      // Bleh
      loginError.value = (canLogin?.value as Exception)?.detail[0]?.msg;
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
      email: email.value,
      timezone: dj.tz.guess(),
    });

    if (inviteCode.value) {
      params.append('invite_code', inviteCode.value);
    }

    const { error, data }: AuthUrlResponse = await call(`fxa_login?${params}`).get().json();

    if (error.value) {
      loginError.value = (data.value as Exception)?.detail[0]?.msg;
      isLoading.value = false;
      return;
    }

    const { url } = data.value as AuthUrl;

    window.location.href = url;
    return;
  }

  const { error }: Error = await user.login(call, email.value, password.value);
  if (error) {
    loginError.value = error as string;
    isLoading.value = false;
    return;
  }

  await router.push('/calendar');
};
</script>

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
            {{ t('label.email') }}
          </span>
            <input
              v-model="email"
              type="email"
              class="mr-6 w-full rounded-md"
              :class="{'mr-4': isFxaAuth}"
              @keydown.enter="isFxaAuth ? login() : null"
            />
          </label>
          <label class="flex flex-col items-center pl-4" v-if="showInviteFlow && !onlyShowInvite">
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
          <div v-if="isFxaAuth && (!showInviteFlow || inviteCode.length > 0)" class="text-center text-sm">{{ t('text.login.continueToFxa') }}</div>
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
