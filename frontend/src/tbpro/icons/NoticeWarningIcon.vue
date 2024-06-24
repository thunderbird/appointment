<script setup>
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
</script>

<template>
  <img src="@/assets/svg/icons/notice-warning.svg" :alt="t('icons.warning')"/>
</template>

<style scoped>

</style>
