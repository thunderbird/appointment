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
      <template v-if="action === waitingListAction.confirm">
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

<script setup>
import {
  inject, onMounted, ref,
} from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { waitingListAction } from '@/definitions';
import ArtSuccessfulBooking from '@/elements/arts/ArtSuccessfulBooking.vue';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';
import { useI18n } from 'vue-i18n';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import ArtLeave from '@/elements/arts/ArtLeave.vue';
import ArtInvalidLink from '@/elements/arts/ArtInvalidLink.vue';

const route = useRoute();
const router = useRouter();

const { t } = useI18n();

// component constants
const call = inject('call');

const isLoading = ref(false);
const isError = ref(false);
const action = ref(null);

const goHome = () => {
  router.push('/');
};

onMounted(async () => {
  isLoading.value = true;
  const { data, error } = await call('waiting-list/action').post({
    token: route.params.token,
  }).json();
  isLoading.value = false;

  if (error?.value) {
    isError.value = true;
    return;
  }

  action.value = data?.value?.action;
});
</script>
