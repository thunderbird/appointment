<template>
  <div class="h-full p-4 flex-center flex-col gap-8">
    <img class="w-full max-w-md" src="/appointment_logo.svg" alt="Appointment Logo" />
    <i18n-t keypath="text.homepageGreetingIntro" tag="label" for="text.homepageGreetingIntroLink">
      <a class="underline" href="https://thunderbird.net" target="_blank">
        {{ $t('text.homepageGreetingIntroLink') }}
      </a>
    </i18n-t>
    <p v-if="!isAuthenticated">{{ $t('text.homepageGreetingUnauthenticated') }}</p>
    <i18n-t
      v-if="isAuthenticated"
      keypath="text.homepageGreetingAuthenticated"
      tag="label"
      for="text.homepageGreetingAuthenticatedLink">
        <a class="underline" href="/settings/calendar" target="_blank">
          {{ $t('text.homepageGreetingAuthenticatedLink') }}
        </a>
    </i18n-t>
  </div>

</template>

<script setup>
import { computed, inject, onMounted } from 'vue';
import { useAuth0 } from '@auth0/auth0-vue';

const refresh = inject('refresh');

const auth = useAuth0();
const isAuthenticated = computed(() => auth.isAuthenticated.value);

// initially load data when component gets remounted
onMounted(async () => {
  await refresh();
});
</script>
