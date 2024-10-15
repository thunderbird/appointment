<script setup lang="ts">
import { inject, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import {
  callKey,
} from '@/keys';
import {
  WaitingListActionResponse,
} from '@/models';
import { posthog, usePosthog } from '@/composables/posthog';
import { MetricEvents, WaitingListAction } from '@/definitions';
import GenericModal from '@/components/GenericModal.vue';
import HomeView from '@/views/HomeView.vue';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import WordMark from '@/elements/WordMark.vue';

// component constants
const route = useRoute();
const router = useRouter();

// component constants
const { t } = useI18n();

// component constants
const call = inject(callKey);

const isLoading = ref(false);
const isError = ref(false);
const errorMsg = ref(null);
const action = ref(null);

onMounted(async () => {
  isLoading.value = true;
  const { data, error }: WaitingListActionResponse = await call('waiting-list/action').post({
    token: route.params.token,
  }).json();
  isLoading.value = false;

  if (error?.value) {
    isError.value = true;
    return;
  }

  action.value = data?.value?.action;

  // They're already a user, and they need to go to settings to delete their account!
  if (data?.value?.redirectToSettings) {
    await router.replace('/settings/account#delete-your-account');
    return;
  }

  if (usePosthog) {
    if (action.value === WaitingListAction.Confirm) {
      posthog.capture(MetricEvents.WaitingListEmailConfirmed, {});
    } else if (action.value === WaitingListAction.Leave) {
      posthog.capture(MetricEvents.WaitingListEmailRemoved, {});
    }
  }
});
</script>

<template>
  <div>
  <home-view></home-view>
  <generic-modal :error-message="errorMsg" @close="() => router.push({name: 'home'})">
    <template v-slot:header>
      <word-mark/>
      <h2 id="title" v-if="isError">
        {{ t('waitingList.errorHeading') }}
      </h2>
      <h2 id="title" v-else-if="action === WaitingListAction.Confirm">
        {{ t('waitingList.confirmHeading') }}
      </h2>
      <h2 id="title" v-else-if="action === WaitingListAction.Leave">
        {{ t('waitingList.leaveHeading') }}
      </h2>
    </template>
    <img class="img is-dark-mode" src="@/assets/svg/ftue-finish-dark.svg" :alt="t('ftue.finishAltText')"/>
    <img class="img is-light-mode" src="@/assets/svg/ftue-finish.svg" :alt="t('ftue.finishAltText')"/>
    <div class="intro-text" v-if="isError">
      <p>{{ t('waitingList.errorInfo') }}</p>
    </div>
    <div class="intro-text" v-else-if="action === WaitingListAction.Confirm">
      <p>{{ t('waitingList.confirmInfo') }}</p>
    </div>
    <div class="intro-text" v-else-if="action === WaitingListAction.Leave">
      <p>{{ t('waitingList.leaveInfo') }}</p>
    </div>
    <div class="intro-text marketing-text">
      <p><strong>{{ t('waitingList.marketing.0') }}</strong></p>
      <p>{{ t('waitingList.marketing.1') }}</p>
    </div>

    <template v-slot:actions>
      <primary-button
        class="btn-close"
        :title="t('label.close')"
        :disabled="isLoading"
        @click="router.push({name: 'home'})"
      >
        {{ t('label.close') }}
      </primary-button>
    </template>
    <template v-slot:footer>
      <router-link :to="{name: 'home'}">{{ t('app.tagline') }}</router-link>
    </template>
  </generic-modal>
  </div>
</template>
<style scoped>
.img {
  margin-top: -1rem;
  margin-bottom: 1rem;
}
.intro-text {
  display: flex;
  flex-direction: column;
  text-align: center;
  max-width:30.0rem;
  margin-bottom: 1rem;
  white-space: break-spaces;
}
.marketing-text {
  margin-bottom: 1.5625rem;
}

@media (--md) {
  .btn-close {
    /* Right align */
    margin-right: 2rem;
    margin-left: auto;
  }
}
</style>
