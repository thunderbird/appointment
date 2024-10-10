<script setup lang="ts">
import { useI18n } from 'vue-i18n';

import SecondaryButton from '@/tbpro/elements/SecondaryButton.vue';
import {
  inject, onMounted, reactive, ref,
} from 'vue';
import { callKey } from '@/keys';
import { useFTUEStore } from '@/stores/ftue-store';
import { storeToRefs } from 'pinia';
import { IconArrowRight } from '@tabler/icons-vue';
import GoogleOauthProvider from '@/components/FTUE/GoogleOauthProvider.vue';
import CalDavProvider from '@/components/FTUE/CalDavProvider.vue';
import CheckboxInput from '@/tbpro/elements/CheckboxInput.vue';

const ftueStore = useFTUEStore();
const {
  hasNextStep, hasPreviousStep, errorMessage,
} = storeToRefs(ftueStore);
const { previousStep, nextStep } = ftueStore;
const { t } = useI18n();
const call = inject(callKey);
const provider = ref('google');

const onNext = async () => {
  await nextStep(call);
};

const onPrevious = () => {
  previousStep();
};

const onSwitch = () => {
  if (provider.value === 'google') {
    provider.value = 'caldav';
  } else {
    provider.value = 'google';
  }
};

const onError = (err: string) => {
  errorMessage.value = err;
};

</script>

<template>
  <div class="content">
    <div class="provider-view">
      <google-oauth-provider @next="onNext" @previous="onPrevious" @switch="onSwitch" :showPrevious="true" :showSwitch="true" v-if="provider === 'google'"></google-oauth-provider>
      <cal-dav-provider @next="onNext" @previous="onPrevious" @switch="onSwitch" @error="onError" :showPrevious="true" :showSwitch="true" v-else-if="provider === 'caldav'"></cal-dav-provider>
    </div>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';
@import '@/assets/styles/mixins.pcss';

.content {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.provider-view {
  width: 100%;
}
</style>
