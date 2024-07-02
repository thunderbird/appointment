<script setup>
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
</script>

<template>
  <img src="@/assets/svg/icons/notice-error.svg" :alt="t('icons.critical')"/>
</template>

<style scoped>

</style>
