<script setup lang="ts">
import { inject, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { createFTUEStore } from '@/stores/ftue-store';
import { createUserStore } from '@/stores/user-store';
import { useI18n } from 'vue-i18n';
import { dayjsKey, callKey } from '@/keys';
import TextInput from '@/tbpro/elements/TextInput.vue';
import SelectInput from '@/tbpro/elements/SelectInput.vue';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';

const { t } = useI18n();
const dj = inject(dayjsKey);
const call = inject(callKey);

const ftueStore = createFTUEStore(call);
const { hasNextStep } = storeToRefs(ftueStore);
const user = createUserStore(call);

// @ts-expect-error ignore type err
// See https://github.com/microsoft/TypeScript/issues/49231
const timezoneOptions = Intl.supportedValuesOf('timeZone').map((timezone: string) => ({
  label: timezone.replaceAll('_', ' '),
  value: timezone,
}));

const formRef = ref<HTMLFormElement>();
const fullName = ref(user.data?.name ?? '');
const username = ref(user.data?.username ?? '');
const timezone = ref(user.data.settings.timezone ?? dj.tz.guess());
const isLoading = ref(false);

// Form validation
const errorFullName = ref<string>(null);
const errorUsername = ref<string>(null);

const onSubmit = async () => {
  isLoading.value = true;
  errorFullName.value = null;
  errorUsername.value = null;

  if (!formRef.value.checkValidity()) {
    isLoading.value = false;
    return;
  }

  if (errorFullName.value || errorUsername.value) {
    isLoading.value = false;
    return;
  }

  const response = await user.updateUser({
    name: fullName.value,
    username: username.value,
    timezone: timezone.value,
  });

  if (response.error) {
    isLoading.value = false;
    return;
  }

  await ftueStore.nextStep();
};

</script>

<template>
  <div class="content">
    <form ref="formRef" autocomplete="off" autofocus @submit.prevent @keyup.enter="onSubmit">
      <text-input name="full-name" v-model="fullName" :required="true" :error="errorFullName">
        {{ t('ftue.fullName') }}
      </text-input>
      <text-input name="username" v-model="username" :required="true" :error="errorUsername">
        {{ t('label.username') }}
      </text-input>
      <select-input
        name="timezone"
        :options="timezoneOptions"
        v-model="timezone"
        :required="true"
      >
        {{ t('label.timeZone') }}
      </select-input>
    </form>
  </div>
  <div class="buttons">
    <primary-button
      class="btn-continue"
      :title="t('label.continue')"
      v-if="hasNextStep"
      @click="onSubmit"
    >
      {{ t('label.continue') }}
    </primary-button>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.content {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 23.75rem;
  gap: 2rem;
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.buttons {
  display: flex;
  width: 100%;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

@media (--md) {
  .buttons {
    justify-content: flex-end;
    position: absolute;
    bottom: 5.75rem;
    margin: 0;
  }
}
</style>
