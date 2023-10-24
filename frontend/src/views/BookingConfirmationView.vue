<template>
  <div class="h-full p-4 flex-center flex-col gap-12">
    <div v-if="isError === null">Loading...</div>
    <div v-else-if="isError === true" class="px-4 flex-center flex-col gap-8 select-none">
      <art-invalid-link class="max-w-sm h-auto my-6" />
      <div class="text-xl font-semibold text-sky-600">
        This link seems to be broken.
      </div>
      <div class="text-gray-800 dark:text-gray-300">
        Some more explanatory text here, carefully revised by Amy.
      </div>
    </div>
    <div v-else>
      <div v-if="confirmed">
        You successfully confirmed the booking.
      </div>
      <div v-else="confirmed">
        You successfully denied the booking.
      </div>
    </div>
  </div>

</template>

<script setup>
import { ref, inject, onMounted } from 'vue';
// import { useAuth0 } from '@auth0/auth0-vue';
import { useRoute } from "vue-router";
import ArtInvalidLink from '@/elements/arts/ArtInvalidLink';

const route = useRoute();
const call = inject('call');

// retrieve all required data from url
const [signedUrl] = window.location.href.split('/confirm/');
const slotId = Number(route.params.slot);
const slotToken = route.params.token;
const confirmed = Boolean(route.params.confirmed);

// const auth = useAuth0();
// const isAuthenticated = computed(() => auth.isAuthenticated.value);
const isError = ref(null);
const event = ref(null);
const attendee = ref(null);

// initially load data when component gets remounted
onMounted(async () => {
  const { error, data } = await call(`apmt/public/${route.params.slug}`).get().json();
  if (error.value) {
    isError.value = true;
  } else {
    isError.value = false;
    event.value = data.value.slot;
    attendee.value = data.value.attendee;
  }
});
</script>
