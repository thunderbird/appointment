<template>
  <!-- fixed header -->
  <header class="fixed h-24 w-full shadow-lg border-b border-gray-300 flex gap-4 items-center">
    <img class="h-10" src="/appointment_logo.svg" alt="Appointment Logo">
    <div class="text-4xl font-thin text-teal-500">Thunderbird</div>
    <div class="text-4xl font-thin text-sky-500">Appointment</div>
  </header>
  <!-- booking page content -->
  <main class="max-w-screen-2xl mx-auto pt-24 flex justify-between items-start select-none">
    <div class="text-xl">{{ t('text.chooseDayTime') }}</div>
  </main>
  <!-- fixed footer with action button -->
  <footer class="fixed bottom-0 h-24 w-full shadow border-t border-gray-300">
    <div class="h-full max-w-screen-2xl mx-auto flex justify-end items-center">
      <primary-button
        class="p-7"
        :label="t('label.confirmSelection')"
        :disabled="true"
        @click="null"
      />
    </div>
  </footer>
</template>

<script setup>
import PrimaryButton from '@/elements/PrimaryButton.vue';
import { useI18n } from "vue-i18n";
const { t } = useI18n();
</script>
