<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useUserStore } from '@/stores/user-store';

const { t } = useI18n();
const user = useUserStore();

const props = defineProps<{
  pendingBookingRequestsCount: number
}>()

const copyBookingUrlLabel = ref(t('label.copyBookingUrl'));
const hasCopied = ref(false);

const copyLink = async () => {
  await navigator.clipboard.writeText(user.myLink);

  copyBookingUrlLabel.value = t('info.copiedToClipboard');
  hasCopied.value = true

  setTimeout(() => {
    copyBookingUrlLabel.value = t('label.copyBookingUrl');
    hasCopied.value = false
  }, 2000);
};
</script>

<template>
  <aside>
    <router-link v-if="props.pendingBookingRequestsCount" data-testid="link-pending-requests" class="link-buton pending"
      :to="{
        path: '/bookings',
        query: {
          unconfirmed: 'true'
        }
      }">
      {{ pendingBookingRequestsCount }} {{ t('label.pendingBookingRequests', pendingBookingRequestsCount) }}
    </router-link>

    <h2
      :class="{ 'has-pending-requests': props.pendingBookingRequestsCount }"
    >
      {{ t('label.whatDoYouWantToDoToday') }}
    </h2>

    <div class="quick-actions-container">
      <button class="link-buton" :class="{ 'copied': hasCopied }" @click="copyLink" data-testid="button-copy-booking-url">
        {{ copyBookingUrlLabel }}
      </button>
      <router-link class="link-buton" to="availability" data-testid="link-change-availability">
        {{ t('label.changeMyAvailability') }}
      </router-link>
      <router-link class="link-buton" to="availability" data-testid="link-modify-booking-page">
        {{ t('label.modifyBookingPage') }}
      </router-link>
    </div>
  </aside>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-block-end: 1.5rem;

  &.has-pending-requests {
    margin-block-start: 3rem;
  }
}

.quick-actions-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.link-buton {
  display: block;
  position: relative;
  cursor: pointer;
  padding: 1rem 1.5rem;
  background-color: var(--colour-neutral-raised);
  text-align: left;

  &.pending {
    border: 3px solid var(--colour-danger-default);
    border-radius: 1rem;
  }

  &.copied {
    background-color: var(--colour-neutral-lower);

    &:hover {
      text-decoration-line: none;
      background-color: var(--colour-neutral-lower);
    }
  }

  &:hover {
    text-decoration-line: underline;
    background-color: var(--colour-neutral-base);
  }
}

@media (--md) {
  aside {
    min-width: 400px;
  }
}
</style>