<template>
  <header
    class="
      fixed h-24 w-full px-4 shadow-lg border-b flex items-center justify-between cursor-default select-none
      bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600
    "
  >
    <div class="flex gap-3 items-center">
      <img class="h-10 mr-2" src="/appointment_logo.svg" alt="Appointment Logo">
      <div class="text-4xl font-thin text-teal-500">Thunderbird</div>
      <div class="text-4xl font-thin text-sky-500">Appointment</div>
    </div>
    <div>
      <primary-button :label="t('label.logIn')" @click="login()" />
    </div>
  </header>
</template>

<script setup>
import { useAuth0 } from '@auth0/auth0-vue';
import { useI18n } from 'vue-i18n';
import PrimaryButton from '@/elements/PrimaryButton';

const { t } = useI18n();
const auth0 = useAuth0();

const login = () => {
  auth0.loginWithRedirect();
};
</script>
