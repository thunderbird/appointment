<template>
  <div class="h-full p-4 flex-center flex-col gap-12">
    <img class="w-full max-w-md" src="/appointment_logo.svg" alt="Appointment Logo" />
    <h2 class="text-2xl pt-6">
      {{ $t('text.homepageGreetingIntro') }}
    </h2>
    <div class="max-w-lg text-center">
      <p v-if="!isAuthenticated">{{ $t('text.homepageGreetingUnauthenticated') }}</p>
      <i18n-t
        v-if="isAuthenticated"
        keypath="text.homepageGreetingAuthenticated"
        tag="label"
        for="text.homepageGreetingAuthenticatedLink"
      >
        <a class="underline" href="/settings/calendar">
          {{ $t('text.homepageGreetingAuthenticatedLink') }}
        </a>
      </i18n-t>
    </div>
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
