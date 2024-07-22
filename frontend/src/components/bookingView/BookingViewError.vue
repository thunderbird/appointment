<template>
  <art-invalid-link class="my-6 h-auto max-w-sm"/>
  <div class="text-xl font-semibold text-sky-600">
    {{ heading ?? t('error.somethingWentWrong') }}
  </div>
  <div class="text-gray-800 dark:text-gray-300">
    {{ body ?? t('error.generalBookingError') }}
  </div>
  <primary-button
    v-if="!user.exists()"
    class="btn-start mt-12 p-7"
    :label="t('label.startUsingTba')"
    @click="router.push({ name: 'home' })"
  />
</template>

<script setup>
import PrimaryButton from '@/elements/PrimaryButton.vue';
import ArtInvalidLink from '@/elements/arts/ArtInvalidLink.vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user-store';

const { t } = useI18n();
const router = useRouter();
const user = useUserStore();

defineProps({
  heading: [String, null],
  body: [String, null],
});

</script>
