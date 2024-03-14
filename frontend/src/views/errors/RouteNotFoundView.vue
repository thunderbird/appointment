<template>
  <div class="flex-center h-full flex-col gap-12 p-4">
    <div class="flex-center flex-col gap-8 px-4">
      <art-invalid-link class="my-6 h-auto max-w-sm"/>
      <div class="text-xl font-semibold text-sky-600">
        {{ t('error.routeNotFound') }}
      </div>
      <primary-button @click="$router.go(-1)">
        {{ t('label.goBack') }}
      </primary-button>
    </div>
  </div>

</template>
<script setup>
import ArtInvalidLink from '@/elements/arts/ArtInvalidLink.vue';
import { useI18n } from 'vue-i18n';
import PrimaryButton from '@/elements/PrimaryButton.vue';

const { t } = useI18n();

</script>
