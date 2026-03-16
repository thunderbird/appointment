<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { LOGIN_REDIRECT_KEY } from '@/definitions';
import ArtInvalidLink from '@/elements/arts/ArtInvalidLink.vue';
import { PrimaryButton } from '@thunderbirdops/services-ui';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();

const goToLogin = () => {
  // Save their intended destination!
  window.sessionStorage?.setItem(LOGIN_REDIRECT_KEY, route.fullPath);
  router.push('/login');
};

</script>

<template>
  <div class="wrapper">
    <art-invalid-link />
    <h1>
      {{ t('error.authenticationRequired') }}
    </h1>
    <primary-button class="btn-login" @click="goToLogin" :title="t('label.logIn')">
      {{ t('label.logIn') }}
    </primary-button>
  </div>
</template>

<style scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  padding: 1rem;

  height: 100%;
}
</style>
