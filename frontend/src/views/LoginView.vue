<script setup lang="ts">
import { inject, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { createUserStore } from '@/stores/user-store';
import {
  dayjsKey, callKey
} from '@/keys';
import {
  BooleanResponse, AuthUrlResponse, AuthUrl, Error, PydanticException, Alert,
} from '@/models';
import GenericModal from '@/components/GenericModal.vue';
import WordMark from '@/elements/WordMark.vue';
import { PrimaryButton, TextInput } from '@thunderbirdops/services-ui';
import { handleFormError } from '@/utils';
import { userManager } from "@/composables/oidcUserManager";
import { isFxaAuth, isOidcAuth, isPasswordAuth } from "@/composables/authSchemes";

// component constants
const { t } = useI18n();
const call = inject(callKey);
const dj = inject(dayjsKey);
const route = useRoute();
const router = useRouter();
const user = createUserStore(call);

const isLoading = ref(false);
const formRef = ref();


enum LoginSteps {
  Login = 1,
  SignUp = 2,
  SignUpConfirm = 3,
}

// form input and error
const email = ref('');
const password = ref('');
const loginStep = ref(LoginSteps.Login);
const loginError = ref<Alert>(null);

onMounted(async () => {
  // Error should be a string value, so don't worry about any obj deconstruction.
  if (route.query.error) {
    const queryError = route.query.error as string;
    loginError.value = { title: t(`login.remoteError.${queryError}`) };
    await router.replace(route.path);
  }

  // This route will be used by the TB Pro Appointment landing page
  // in its login button. This will redirect the user to the OIDC login page
  // if they are not authenticated, otherwise it will redirect to the dashboard.
  if (isOidcAuth) {
    if (user.authenticated) {
      await router.push({ name: 'dashboard' });
    } else {
      await userManager.signinRedirect({});
    }
  }
});


const login = async () => {
  isLoading.value = true;

  // If they come here the first time we check if they're allowed to login
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
  }


  if (isOidcAuth) {
    await userManager.signinRedirect({
      login_hint: email.value,
    });
  } else if (isFxaAuth) {
    const apiUrl = 'fxa_login';
    const params = new URLSearchParams({
      email: email.value,
      timezone: dj.tz.guess(),
    });

    const { error, data }: AuthUrlResponse = await call(`${apiUrl}?${params}`).get().json();

    if (error.value) {
      loginError.value = handleFormError(t, formRef, data.value as PydanticException);
      isLoading.value = false;
      return;
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

  login();
};
</script>

<template>
  <!-- If the user is coming from the TB Pro Appointment landing page,
      and the auth scheme is OIDC we don't need to show anything here since we are redirecting. -->
  <template v-if="isOidcAuth">
    <div class="full-height-placeholder" />
  </template>

  <template v-else>
    <div class="full-height-placeholder" />
    <generic-modal :error-message="loginError" @close="() => router.push({name: 'home'})" :closable="false">
      <template v-slot:header>
        <word-mark/>
      </template>
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
          >{{ t('login.form.email') }}
          </text-input>
          <text-input
            v-if="isPasswordAuth"
            name="password"
            v-model="password"
            :required="true"
            type="password"
            data-testid="login-password-input"
          >{{ t('label.password') }}
          </text-input>
        </form>
      </div>
      <template v-slot:actions>
        <primary-button
          class="btn-continue"
          :title="t('label.login')"
          :disabled="isLoading"
          @click="onEnter()"
          data-testid="login-continue-btn"
        >
          {{ t('label.logIn') }}
        </primary-button>
      </template>
      <template v-slot:footer>
        <router-link :to="{name: 'home'}">{{ t('app.tagline') }}</router-link>
      </template>
    </generic-modal>
  </template>
</template>
<style scoped>
@import '@/assets/styles/custom-media.pcss';

.full-height-placeholder {
  /* 68px is the height of the navbar, 365px is the height of the modal */
  height: calc(100dvh - 68px - 365px);
}

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
