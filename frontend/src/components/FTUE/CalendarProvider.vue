<script setup lang="ts">
import {
  inject, ref,
} from 'vue';
import { callKey } from '@/keys';
import { createFTUEStore } from '@/stores/ftue-store';
import { storeToRefs } from 'pinia';
import { Alert } from '@/models';
import GoogleOauthProvider from '@/components/FTUE/GoogleOauthProvider.vue';
import CalDavProvider from '@/components/FTUE/CalDavProvider.vue';

const call = inject(callKey);
const ftueStore = createFTUEStore(call);
const { errorMessage } = storeToRefs(ftueStore);
const provider = ref('google');

const onNext = async () => {
  await ftueStore.nextStep();
};

const onPrevious = () => {
  ftueStore.previousStep();
};

const onSwitch = () => {
  if (provider.value === 'google') {
    provider.value = 'caldav';
  } else {
    provider.value = 'google';
  }
};

const onError = (alert: Alert) => {
  errorMessage.value = alert;
};

</script>

<template>
  <div class="content">
    <div class="provider-view">
      <google-oauth-provider
        v-if="provider === 'google'"
        @next="onNext"
        @previous="onPrevious"
        @switch="onSwitch"
        :showPrevious="true"
        :showSwitch="true"
      />
      <cal-dav-provider
        v-else-if="provider === 'caldav'"
        @next="onNext"
        @previous="onPrevious"
        @switch="onSwitch"
        @error="onError"
        :showPrevious="true"
        :showSwitch="true"
      />
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
