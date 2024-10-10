<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import {
  computed,
  inject, ref,
} from 'vue';
import { callKey } from '@/keys';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import TextInput from '@/tbpro/elements/TextInput.vue';
import { CalendarListResponse, PydanticException } from '@/models';
import { clearFormErrors, handleFormError } from '@/utils';
import SecondaryButton from '@/tbpro/elements/SecondaryButton.vue';

const { t } = useI18n();
const call = inject(callKey);
const isLoading = ref(false);
const principal = ref({
  url: '',
  user: '',
  password: '',
});

/**
 * Default to the domain of an email address from username
 */
const locationPreview = computed(() => {
  const splitAddress = principal.value.user.split('@');
  if (splitAddress.length > 1) {
    return splitAddress[1];
  }
  return '';
});

// component properties
interface Props {
  showPrevious: boolean,
  showSwitch: boolean,
}
withDefaults(defineProps<Props>(), {
  showPrevious: false,
  showSwitch: false,
});
const emits = defineEmits(['next', 'error', 'previous', 'switch']);
const formRef = ref();

/**
 * Submit the credentials, this will perform a dns check to see if there's any
 * caldav server specified via SRV, if that fails then it will attempt to
 * connect to the server listed.
 */
const onSubmit = async () => {
  clearFormErrors(formRef);
  if (!formRef.value.checkValidity()) {
    formRef.value.reportValidity();
    return;
  }

  isLoading.value = true;

  const requestData = {
    url: principal.value.url || locationPreview.value,
    user: principal.value.user,
    password: principal.value.password,
  };

  const { error, data }: CalendarListResponse = await call('/caldav/auth').post(requestData).json();

  isLoading.value = false;

  if (!error.value) {
    emits('next');
  } else {
    const err = handleFormError(t, formRef, data?.value as PydanticException);
    if (err) {
      // Emit a form-level error event if there's a problem here
      emits('error', err);
    }
  }
};
</script>
<template>
  <div class="content">
      <form class="form" ref="formRef" @submit.prevent @keyup.enter="() => onSubmit()">
        <text-input :disabled="isLoading" name="user" v-model="principal.user" help="This is usually an email address." :required="true">
          Username
        </text-input>
        <text-input :disabled="isLoading" :placeholder="locationPreview" name="url" help="The URL or hostname we will use to connect to your calendars." v-model="principal.url">
          Location
        </text-input>
        <text-input :disabled="isLoading" type="password" name="password" help="This is usually not your email address password, but an 'App Password'." v-model="principal.password">
          Password
        </text-input>
      </form>
      <div class="buttons">
        <secondary-button class="btn-switch" @click="emits('switch')" v-if="showSwitch">
        Switch to Google Calendar
        </secondary-button>
        <secondary-button @click="emits('previous')" v-if="showPrevious">
        Back
        </secondary-button>
        <primary-button
          :label="'Connect a Caldav principal server'"
          :disabled="isLoading"
          @click="onSubmit"
        >{{ t('label.connect') }}</primary-button>
      </div>
    </div>
</template>
<style scoped>
@import '@/assets/styles/custom-media.pcss';
@import '@/assets/styles/mixins.pcss';

.content {
  display: flex;
  flex-direction: column;
  margin: auto;
  gap: 1rem;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin: auto;
}
.btn-switch {
  margin-left: 2rem;
  margin-right: auto;
}
.buttons {
  display: flex;
  width: 100%;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
  left: auto;
  right: auto;
}
@media (--md) {
  .buttons {
    justify-content: flex-end;
    position: absolute;
    right: 2rem;
    bottom: 5.75rem;
    margin: 0;
  }
}
</style>
