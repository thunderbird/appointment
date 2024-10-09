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

const ftueStore = useFTUEStore();
const {
  hasNextStep, hasPreviousStep, errorMessage,
} = storeToRefs(ftueStore);
const { previousStep, nextStep } = ftueStore;
const { t } = useI18n();
const call = inject(callKey);
const isLoading = ref(false);
const provider = ref('google');

</script>

<template>
  <div class="content">
    <div>
      <ul class="provider-selector">
        <li @click="provider = 'google'">Google Calendar</li>
        <li @click="provider = 'caldav'">CalDav</li>
      </ul>
    </div>
    <div class="provider-view">
      <google-oauth-provider v-if="provider === 'google'"></google-oauth-provider>
      <cal-dav-provider v-else-if="provider === 'caldav'"></cal-dav-provider>
    </div>
  </div>
</template>

<style scoped>
  .content {
    width: 100%;
    display: flex;
    gap: 2rem;
  }
  .provider-selector {
    width: 4rem;

    display: flex;
    flex-direction: column;
    gap: 2rem;

    /* temp */
    li {
      cursor: pointer;
    }
  }
  .provider-view {
    width: 100%;
  }
</style>
