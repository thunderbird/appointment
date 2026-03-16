<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import ArtInvalidLink from '@/elements/arts/ArtInvalidLink.vue';
import { PrimaryButton } from '@thunderbirdops/services-ui';

const { t } = useI18n();
</script>

<template>
  <div class="wrapper">
    <art-invalid-link />
    <h1>
      {{ t('error.routeNotFound') }}
    </h1>
    <primary-button class="btn-back" @click="$router.go(-1)" :title="t('label.goBack')">
      {{ t('label.goBack') }}
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
