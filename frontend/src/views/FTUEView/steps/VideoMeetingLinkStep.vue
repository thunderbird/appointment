<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { useFTUEStore } from '@/stores/ftue-store';

import StepTitle from '../components/StepTitle.vue';

const { t } = useI18n();
const ftueStore = useFTUEStore();
</script>

<template>
  <step-title :title="t('ftue.videoMeetingLink')" />
</template>