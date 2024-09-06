<script setup lang="ts">
import { inject, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user-store';
import {
  dayjsKey, callKey, isPasswordAuthKey, isFxaAuthKey,
} from '@/keys';
import {
  BooleanResponse,
  AuthUrlResponse,
  Exception,
  AuthUrl,
  Error,
  PydanticExceptionDetail,
  ExceptionDetail,
  PydanticException,
} from '@/models';
import { posthog, usePosthog } from '@/composables/posthog';
import { MetricEvents } from '@/definitions';
import GenericModal from '@/components/GenericModal.vue';
import HomeView from '@/views/HomeView.vue';
import TextInput from '@/tbpro/elements/TextInput.vue';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import WordMark from '@/elements/WordMark.vue';

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
const loginError = ref<string>(null);

onMounted(() => {
  if (route.name === 'join-the-waiting-list') {
    hideInviteField.value = true;
    loginStep.value = LoginSteps.SignUp;
  }
});

const handleFormError = (errObj: PydanticException) => {
  const { detail } = errObj;
  const fields = formRef.value.elements;

  detail.forEach((err) => {
    const name = err?.loc[1];
    if (name) {
      fields[name].setCustomValidity(err.ctx.reason);
    }
  });

  // Finally report it!
  formRef.value.reportValidity();
};

/**
 * Sign up for the beta / waiting list
 */
const signUp = async () => {
  if (!email.value) {
    return;
  }

  isLoading.value = true;
  loginError.value = '';
  const { data, error }: BooleanResponse = await call('waiting-list/join').post({
    email: email.value,
  }).json();

  if (error?.value) {
    // Handle error
    handleFormError(data.value as PydanticException);
    isLoading.value = false;
    return;
  }

  if (!data.value) {
    loginError.value = t('waitingList.signUpAlreadyExists');

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

    console.log(error.value, canLogin.value);
    if (error?.value) {
      // Handle error
      handleFormError(canLogin.value as PydanticException);
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
      handleFormError(data.value as PydanticException);
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

  const { error }: Error = await user.login(call, email.value, password.value);
  if (error) {
    loginError.value = error as string;
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

  if (loginStep.value === LoginSteps.SignUp || hideInviteField.value) {
    signUp();
  } else {
    login();
  }
};
</script>

<template>
  <div>
  <home-view></home-view>
  <generic-modal :error-message="loginError">
    <template v-slot:header>
      <word-mark/>
      <h2 id="title" v-if="loginStep === LoginSteps.Login">
        Simplify your day – just enter your email:
      </h2>
      <h2 id="title" v-else-if="loginStep === LoginSteps.SignUp">
        Have an invite code? Enter it here
      </h2>
      <h2 id="title" v-else>
        Complete your sign up
      </h2>
    </template>
    <div class="intro-text" v-if="loginStep === LoginSteps.Login">
      <p><strong>Returning?</strong> We'll recognize you and direct you to your account.</p>
      <p><strong>New?</strong> We'll help you set up quickly.</p>
    </div>
    <div class="intro-text" v-if="loginStep === LoginSteps.SignUpConfirm">
      <p><strong>Please confirm your email to join our waiting list.</strong></p>
      <p>Check your inbox for more information shortly.</p>
    </div>
    <div class="form-body">
      <form v-if="loginStep !== LoginSteps.SignUpConfirm" class="form" ref="formRef" autocomplete="off" @submit.prevent @keyup.enter="() => onEnter()">
        <text-input name="email" v-model="email" :required="true" :help="loginStep === LoginSteps.Login || hideInviteField ? 'Your privacy is important to us.' : null">{{ t('label.email') }}</text-input>
        <text-input v-if="isPasswordAuth" name="password" v-model="password" :required="true">{{ t('label.password') }}</text-input>
        <text-input v-if="loginStep === LoginSteps.SignUp && !hideInviteField" name="inviteCode" v-model="inviteCode" help="If you don't have an invite code, add your email to our waiting list">{{ t('label.inviteCode') }}</text-input>
      </form>
    </div>
    <template v-slot:actions>
      <primary-button
        class="btn-continue"
        :title="t('label.continue')"
        @click="onEnter()"
        v-if="loginStep !== LoginSteps.SignUpConfirm"
      >
        {{ t('label.continue') }}
      </primary-button>
      <primary-button
        class="btn-close"
        :title="t('label.close')"
        @click="router.push({name: 'home'})"
        v-else
      >
        {{ t('label.close') }}
      </primary-button>
    </template>
    <template v-slot:footer>
      <router-link :to="{name: 'home'}">Plan less, do more</router-link>
    </template>
  </generic-modal>
  </div>
</template>
<style scoped>
.intro-text {
  display: flex;
  flex-direction: column;
  text-align: center;
  gap: 0.983125rem;
  margin-bottom: 1.5625rem;
}
.form-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 23.75rem;
}

.btn-continue, .btn-close {
  /* Right align */
  margin-right: 2rem;
  margin-left: auto;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>
