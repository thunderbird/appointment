<script setup lang="ts">
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
  <h1>{{ heading ?? t('error.somethingWentWrong') }}</h1>
  <p>{{ body ?? t('error.generalBookingError') }}</p>
</template>

<style scoped>
h1 {
  font-size: 1.25rem;
  line-height: 1.75rem;
  font-weight: 600;
  font-family: metropolis, sans-serif;
  color: var(--colour-primary-default);
}

p {
  color: var(--colour-ti-secondary);
}
</style>