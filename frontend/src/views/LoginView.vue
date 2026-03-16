<script setup lang="ts">
import { inject, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { createUserStore } from '@/stores/user-store';
import { dayjsKey, callKey } from '@/keys';
import { BooleanResponse, AuthUrlResponse, AuthUrl, Error, PydanticException, Alert } from '@/models';
import { PrimaryButton, TextInput, NoticeBar, NoticeBarTypes, IconButton } from '@thunderbirdops/services-ui';
import { handleFormError } from '@/utils';
import { userManager } from "@/composables/oidcUserManager";
import { isFxaAuth, isOidcAuth, isPasswordAuth } from "@/composables/authSchemes";
import { PhX } from '@phosphor-icons/vue';

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
  <!--
    If the user is coming from the TB Pro Appointment landing page, and the auth scheme is OIDC
    we don't need to show anything here since we are redirecting.
  -->
  <div v-if="!isOidcAuth" class="login-wrapper">
    <notice-bar v-if="loginError" class="notice-bar" :type="NoticeBarTypes.Critical">
      {{ loginError.title }}
      <template #cta>
        <icon-button @click="loginError = null" :title="t('label.close')">
          <ph-x />
        </icon-button>
      </template>
    </notice-bar>

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
      >
        {{ t('login.form.email') }}
      </text-input>

      <text-input
        v-if="isPasswordAuth"
        name="password"
        v-model="password"
        :required="true"
        type="password"
        data-testid="login-password-input"
      >
        {{ t('label.password') }}
      </text-input>
      
      <primary-button
        class="btn-continue"
        :title="t('label.login')"
        :disabled="isLoading"
        @click="onEnter()"
        data-testid="login-continue-btn"
      >
        {{ t('label.logIn') }}
      </primary-button>
    </form>

  </div>
</template>
<style scoped>
@import '@/assets/styles/custom-media.pcss';

.login-wrapper {
  max-width: 24rem;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.notice-bar {
  margin-bottom: 1rem;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (--md) {
  .btn-continue {
    margin-left: auto;
  }
}
</style>
