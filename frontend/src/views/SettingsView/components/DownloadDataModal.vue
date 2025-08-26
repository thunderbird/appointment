<script setup lang="ts">
import { inject, ref, useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';
import { TextInput, PrimaryButton } from '@thunderbirdops/services-ui';
import { isFxaAuth, isOidcAuth, isPasswordAuth } from "@/composables/authSchemes";
import { Alert, PydanticException, Error, AuthUrlResponse } from '@/models';
import { useUserStore } from '@/stores/user-store';
import { handleFormError } from '@/utils';
import { AlertSchemes } from "@/definitions";
import AlertBox from '@/elements/AlertBox.vue';
import { userManager } from '@/composables/oidcUserManager';
import { callKey, dayjsKey } from '@/keys';

const { t } = useI18n();
const call = inject(callKey);
const dj = inject(dayjsKey);
const userStore = useUserStore();

const formRef = useTemplateRef<HTMLFormElement>('formRef');
const email = ref('');
const password = ref('');
const isLoading = ref(false);
const loginError = ref<Alert>(null);

const props = defineProps<{
  onLoginSuccessful: () => void,
}>();

async function onSubmit() {
  isLoading.value = true;

  if (isOidcAuth) {
    // TODO: Can we redirect for the Settings view specifically?
    // How to catch errors?
    await userManager.signinRedirect({
      prompt: 'login',
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
  } else if (isPasswordAuth) {
    if (!formRef.value.checkValidity()) {
      formRef.value.reportValidity();
      isLoading.value = false;
      return;
    }

    const { error }: Error = await userStore.refreshAccessToken(email.value, password.value);

    if (error) {
      let errObj = error as PydanticException;
      if (typeof error === 'string') {
        errObj = { detail: error };
      }

      loginError.value = handleFormError(t, formRef, errObj);
      isLoading.value = false;
      return;
    }
  }

  loginError.value = null;
  isLoading.value = false;

  // Actually download the data (defined in AccountSettings.vue)
  props.onLoginSuccessful();
};
</script>

<template>
  <p>{{ t('label.reauthenticateToDownloadData') }}</p>

  <form
    ref="formRef"
    autocomplete="off"
    @submit.prevent
    @keyup.enter="onSubmit"
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

    <primary-button @click="onSubmit">
      {{ t('label.download') }}
    </primary-button>

    <alert-box
      v-if="loginError"
      :alert="loginError"
      :scheme="AlertSchemes.Error"
      @close="loginError = null"
    />
  </form>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

p {
  margin-block-end: 1.5rem;
}

form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
}

@media (--md) {
  form {
    width: 50%;
  }
}
</style>