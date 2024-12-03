<script setup lang="ts">
import { inject, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { createUserStore } from '@/stores/user-store';
import {
  dayjsKey, callKey, isPasswordAuthKey, isFxaAuthKey, isAccountsAuthKey,
} from '@/keys';
import {
  BooleanResponse, AuthUrlResponse, AuthUrl, Error, PydanticException, Alert,
} from '@/models';
import { posthog, usePosthog } from '@/composables/posthog';
import { MetricEvents } from '@/definitions';
import GenericModal from '@/components/GenericModal.vue';
import HomeView from '@/views/HomeView.vue';
import TextInput from '@/tbpro/elements/TextInput.vue';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import WordMark from '@/elements/WordMark.vue';
import { handleFormError } from '@/utils';

// component constants
const { t } = useI18n();
const call = inject(callKey);
const dj = inject(dayjsKey);
const route = useRoute();
const router = useRouter();
const isPasswordAuth = inject(isPasswordAuthKey);
const isFxaAuth = inject(isFxaAuthKey);
const isAccountsAuth = inject(isAccountsAuthKey);
const user = createUserStore(call);

// Don't show the invite code field, only the "Join the waiting list" part
const hideInviteField = ref(false);
const isLoading = ref(false);
const formRef = ref();

// eslint-disable-next-line no-shadow
enum LoginSteps {
  Login = 1,
  SignUp = 2,
  SignUpConfirm = 3,
}

// form input and error
const email = ref('');
const password = ref('');
const inviteCode = ref('');
const loginStep = ref(LoginSteps.Login);
const loginError = ref<Alert>(null);

onMounted(async () => {
  // Error should be a string value, so don't worry about any obj deconstruction.
  if (route.query.error) {
    const queryError = route.query.error as string;
    loginError.value = { title: t(`login.remoteError.${queryError}`) };
    await router.replace(route.path);
  }

  if (route.name === 'join-the-waiting-list') {
    hideInviteField.value = true;
    loginStep.value = LoginSteps.SignUp;
  }
});

/**
 * Sign up for the beta / waiting list
 */
const signUp = async () => {
  if (!email.value) {
    return;
  }

  isLoading.value = true;
  loginError.value = null;
  const { data, error }: BooleanResponse = await call('waiting-list/join').post({
    email: email.value,
  }).json();

  if (error?.value) {
    // Handle error
    loginError.value = handleFormError(t, formRef, data.value as PydanticException);
    isLoading.value = false;
    return;
  }

  if (!data.value) {
    loginError.value = { title: t('waitingList.signUpAlreadyExists') };

    if (usePosthog) {
      posthog.capture(MetricEvents.SignUpAlreadyExists, {
        waitingList: true,
        for: 'beta',
      });
    }
  } else {
    // Advance them to the "Check your email" step
    loginStep.value = LoginSteps.SignUpConfirm;

    if (usePosthog) {
      posthog.capture(MetricEvents.SignUp, {
        waitingList: true,
        for: 'beta',
      });
    }
  }

  isLoading.value = false;
};

const login = async () => {
  isLoading.value = true;

  // If they come here the first time we check if they're allowed to login
  // If they come here a second time after not being allowed it's because they have an invite code.
  if (loginStep.value === LoginSteps.Login) {
    const { data: canLogin, error }: BooleanResponse = await call('can-login').post({
      email: email.value,
    }).json();

    if (error?.value) {
      // Handle error
      loginError.value = handleFormError(t, formRef, canLogin.value as PydanticException);
      isLoading.value = false;
      return;
    }

    if (!canLogin.value) {
      // Advance them to the SignUp step (waiting list right now!)
      loginStep.value = LoginSteps.SignUp;
      isLoading.value = false;
      return;
    }
  }

  if (isFxaAuth || isAccountsAuth) {
    const apiUrl = isFxaAuth ? 'fxa_login' : 'auth/accounts';
    const params = new URLSearchParams({
      email: email.value,
      timezone: dj.tz.guess(),
    });

    if (inviteCode.value) {
      params.append('invite_code', inviteCode.value.trim());
    }

    const { error, data }: AuthUrlResponse = await call(`${apiUrl}?${params}`).get().json();

    if (error.value) {
      loginError.value = handleFormError(t, formRef, data.value as PydanticException);
      isLoading.value = false;
      return;
    }

    if (usePosthog) {
      posthog.capture(MetricEvents.Login, {
        inviteCodeUsed: !!inviteCode.value,
      });
    }

    const { url } = data.value as AuthUrl;

    window.location.href = url;
    return;
  }

  const { error }: Error = await user.login(email.value, password.value);
  if (error) {
    let errObj = error as PydanticException;
    if (typeof error === 'string') {
      errObj = { detail: error };
    }

    loginError.value = handleFormError(t, formRef, errObj);
    isLoading.value = false;
    return;
  }

  await router.push({ name: 'dashboard' });
};

/**
 * What to do when hitting the enter key on a particular input
 */
const onEnter = () => {
  // Validate the form first
  loginError.value = null;
  if (!formRef.value.checkValidity()) {
    formRef.value.reportValidity();
    isLoading.value = false;
    return;
  }

  if ((loginStep.value === LoginSteps.SignUp || hideInviteField.value) && inviteCode.value === '') {
    signUp();
  } else {
    login();
  }
};
</script>

<template>
  <div>
    <home-view></home-view>
    <generic-modal :error-message="loginError" @close="() => router.push({name: 'home'})">
      <template v-slot:header>
        <word-mark/>
        <h2 id="title" v-if="hideInviteField">
          {{ t('login.waitingListSignUp.title') }}
        </h2>
        <h2 id="title" v-else-if="loginStep === LoginSteps.Login">
          {{ t('login.login.title') }}
        </h2>
        <h2 id="title" v-else-if="loginStep === LoginSteps.SignUp">
          {{ t('login.signUp.title') }}
        </h2>
        <h2 id="title" v-else>
          {{ t('login.confirm.title') }}
        </h2>
      </template>
      <div class="intro-text" v-if="loginStep === LoginSteps.SignUpConfirm">
        <p><strong>{{ t('login.confirm.intro.0') }}</strong></p>
        <p>{{ t('login.confirm.intro.1') }}</p>
      </div>
      <div class="form-body">
        <form
          v-if="loginStep !== LoginSteps.SignUpConfirm"
          class="form"
          ref="formRef"
          autocomplete="off"
          @submit.prevent
          @keyup.enter="() => onEnter()"
        >
          <text-input
            name="email"
            v-model="email"
            :required="true"
            data-testid="login-email-input"
          >{{ t('login.form.email') }}</text-input>
          <text-input
            v-if="isPasswordAuth"
            name="password"
            v-model="password"
            :required="true"
            type="password"
            data-testid="login-password-input"
          >{{ t('label.password') }}</text-input>
          <text-input
            v-if="loginStep === LoginSteps.SignUp && !hideInviteField"
            name="inviteCode"
            v-model="inviteCode"
            :help="t('login.form.no-invite-code')"
            data-testid="login-invite-code-input"
          >{{ t('label.inviteCode', { 'count': 1 }) }}</text-input>
        </form>
      </div>
      <template v-slot:actions>
        <primary-button
          class="btn-continue"
          :title="t('label.continue')"
          :disabled="isLoading"
          @click="onEnter()"
          v-if="loginStep !== LoginSteps.SignUpConfirm"
          data-testid="login-continue-btn"
        >
          {{ t('label.continue') }}
        </primary-button>
        <primary-button
          class="btn-close"
          :title="t('label.close')"
          :disabled="isLoading"
          @click="router.push({name: 'home'})"
          v-else
          data-testid="login-close-btn"
        >
          {{ t('label.close') }}
        </primary-button>
      </template>
      <template v-slot:footer>
        <router-link :to="{name: 'home'}">{{ t('app.tagline') }}</router-link>
      </template>
    </generic-modal>
  </div>
</template>
<style scoped>
@import '@/assets/styles/custom-media.pcss';

.intro-text {
  display: flex;
  flex-direction: column;
  text-align: center;
  gap: 0.983125rem;
  margin-bottom: 1.5625rem;
}

/* Tweak the generic-modal's modal-body style */
:deep(.modal-body) {
  margin-top: 1rem;
}

.form-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (--md) {
  .form-body {
    max-width: 23.75rem;
  }

  .btn-continue, .btn-close {
    /* Right align */
    margin-right: 2rem;
    margin-left: auto;
  }
}
</style>
