<template>
  <art-invalid-link class="my-6 h-auto max-w-sm"/>
  <div class="text-xl font-semibold text-sky-600">
    {{ heading ?? t('info.bookingLinkHasAlreadyBeenUsed') }}
  </div>
  <div class="text-gray-800 dark:text-gray-300">
    {{ body ?? t('info.bookedPleaseCheckEmail') }}
  </div>
  <primary-button
    class="mt-12 p-7"
    :label="t('label.startUsingTba')"
    @click="router.push({ name: 'home' })"
  />
</template>

<script setup>
import PrimaryButton from '@/elements/PrimaryButton.vue';
import ArtInvalidLink from '@/elements/arts/ArtInvalidLink.vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

const { t } = useI18n();
const router = useRouter();

defineProps({
  heading: [String, null],
  body: [String, null],
});

</script>
