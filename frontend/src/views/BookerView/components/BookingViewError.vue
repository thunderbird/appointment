<script setup lang="ts">
import ArtInvalidLink from '@/elements/arts/ArtInvalidLink.vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

// component properties
interface Props {
  heading?: string | null;
  body?: string | null;
}
defineProps<Props>();
</script>

<template>
  <art-invalid-link class="my-6 h-auto max-w-sm"/>
  <div class="text-xl font-semibold text-sky-600">
    {{ heading ?? t('error.somethingWentWrong') }}
  </div>
  <div class="text-gray-800 dark:text-gray-300">
    {{ body ?? t('error.generalBookingError') }}
  </div>
</template>
