<template>
  <div class="flex-center h-full flex-col gap-12 p-4">
    <div class="flex-center flex-col gap-8 px-4">
      <art-invalid-link class="my-6 h-auto max-w-sm"/>
      <div class="text-xl font-semibold text-sky-600">
        {{ t('error.authenticationRequired') }}
      </div>
      <primary-button @click="goToLogin">
        {{ t('label.logIn') }}
      </primary-button>
    </div>
  </div>

</template>
<script setup>
import ArtInvalidLink from '@/elements/arts/ArtInvalidLink.vue';
import { useI18n } from 'vue-i18n';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import { useRoute, useRouter } from 'vue-router';
import { loginRedirectKey } from '@/definitions';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();

const goToLogin = () => {
  // Save their intended destination!
  window.sessionStorage?.setItem(loginRedirectKey, route.fullPath);
  router.push('/login');
};

</script>
