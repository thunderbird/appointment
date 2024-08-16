<script setup lang="ts">
import { inject, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {MetricEvents, WaitingListAction} from '@/definitions';
import { WaitingListActionResponse } from '@/models';
import { useI18n } from 'vue-i18n';
import { callKey } from '@/keys';
import ArtSuccessfulBooking from '@/elements/arts/ArtSuccessfulBooking.vue';
import ArtLeave from '@/elements/arts/ArtLeave.vue';
import ArtInvalidLink from '@/elements/arts/ArtInvalidLink.vue';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import {posthog, usePosthog} from "@/composables/posthog";

const route = useRoute();
const router = useRouter();

const { t } = useI18n();

// component constants
const call = inject(callKey);

const isLoading = ref(false);
const isError = ref(false);
const action = ref(null);

const goHome = () => {
  router.push('/');
};

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
  <div class="flex-center h-full flex-col gap-12 p-4">
    <div v-if="isLoading">
      <loading-spinner/>
    </div>
    <div v-else-if="isError" class="flex-center flex-col gap-8 px-4">
      <art-invalid-link class="my-6 h-auto max-w-sm"/>
      <div class="text-xl font-semibold text-sky-600">
        {{ t('waitingList.errorHeading') }}
      </div>
      <div class="text-center text-gray-800 dark:text-gray-300">
        {{ t('waitingList.errorInfo') }}<br>
      </div>
      <primary-button
        :label="t('label.home')"
        class="btn-back"
        @click="goHome"
        :title="t('label.home')"
      />
    </div>
    <div v-else class="flex-center flex-col gap-8 px-4">
      <template v-if="action === WaitingListAction.Confirm">
        <art-successful-booking class="my-6 h-auto max-w-sm"/>
        <div class="text-xl font-semibold text-sky-600">
          {{ t('waitingList.confirmHeading') }}
        </div>
        <div class="text-center text-gray-800 dark:text-gray-300">
          {{ t('waitingList.confirmInfo') }}<br>
        </div>
        <primary-button
          :label="t('label.home')"
          class="btn-back"
          @click="goHome"
          :title="t('label.home')"
        />
      </template>
      <template v-else>
        <art-leave class="my-6 h-auto max-w-sm"/>
        <div class="text-xl font-semibold text-sky-600">
          {{ t('waitingList.leaveHeading') }}
        </div>
        <div class="text-center text-gray-800 dark:text-gray-300">
          {{ t('waitingList.leaveInfo') }}
        </div>
        <primary-button
          :label="t('label.home')"
          class="btn-back"
          @click="goHome"
          :title="t('label.home')"
        />
      </template>
    </div>
  </div>
</template>
