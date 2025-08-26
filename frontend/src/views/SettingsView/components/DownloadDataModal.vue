<script setup lang="ts">
import { ref, useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';
import { TextInput, PrimaryButton } from '@thunderbirdops/services-ui';
import { isPasswordAuth } from "@/composables/authSchemes";
import { Alert, PydanticException, Error } from '@/models';
import { useUserStore } from '@/stores/user-store';
import { handleFormError } from '@/utils';
import { AlertSchemes } from "@/definitions";
import AlertBox from '@/elements/AlertBox.vue';

const { t } = useI18n();
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
  loginError.value = null;

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

  loginError.value = null;
  isLoading.value = false;

  props.onLoginSuccessful();
};
</script>

<template>
  <p>{{ t('label.reauthenticateToDownloadData') }}</p>

  <form
    ref="formRef"
    autocomplete="off"
    @submit.prevent
    @keyup.enter="() => onSubmit()"
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