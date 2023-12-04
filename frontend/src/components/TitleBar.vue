<template>
  <header
    class="
      z-50 h-16 w-full px-4 flex items-center justify-between cursor-default select-none
      bg-white dark:bg-gray-700
    "
  >
    <div class="mr-0 ml-auto hidden md:block">
      <primary-button :label="t('label.logIn')" href="/login" />
    </div>
  </header>
</template>

<script setup>
import { useI18n } from 'vue-i18n';
import PrimaryButton from '@/elements/PrimaryButton';

const { t } = useI18n();
</script>
