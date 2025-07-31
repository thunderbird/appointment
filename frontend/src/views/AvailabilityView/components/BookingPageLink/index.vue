<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { IconCopy, IconRefresh } from '@tabler/icons-vue';
import { TextInput } from '@thunderbirdops/services-ui';
import { MetricEvents } from '@/definitions';
import { useUserStore } from '@/stores/user-store';
import ConfirmationModal from '@/components/ConfirmationModal.vue';
import { posthog, usePosthog } from '@/composables/posthog';

const { t } = useI18n();

const userStore = useUserStore();

const refreshLinkModalOpen = ref(false);
const copyButtonLabel = ref(t('label.copy'));

function openRefreshLinkModal() {
  refreshLinkModalOpen.value = true;
}

function closeRefreshLinkModal() {
  refreshLinkModalOpen.value = false;
}

async function refreshLinkConfirm() {
  await userStore.changeSignedUrl();
  await userStore.profile();

  closeRefreshLinkModal();

  if (usePosthog) {
    posthog.capture(MetricEvents.RefreshLink);
  }
};

async function copyLink() {
  await navigator.clipboard.writeText(userStore.myLink);

  copyButtonLabel.value = t('label.copied');

  setTimeout(() => {
    copyButtonLabel.value = t('label.copy');
  }, 2000);
};
</script>

<script lang="ts">
export default {
  name: 'BookingPageLink'
}
</script>

<template>
  <header>
    <h2>{{ t('label.bookingPageLink') }}</h2>
  </header>

  <!-- Customize your link -->
  <text-input
    name="customizeLink"
    class="customize-link-input"
    outer-prefix="apmt.day/username"
    v-model="userStore.mySlug"
  >
    {{ t('label.customizeYourLink') }}:
    <button @click="openRefreshLinkModal">
      <icon-refresh size="20" />
    </button>
  </text-input>

  <!-- Share your link -->
  <div>
    <h3>{{ t('label.shareYourLink') }}:</h3>
    <div class="share-link-container">
      <p>{{ userStore.myLink }}</p>
      <button @click="copyLink">
        <icon-copy size="12" />
        {{ copyButtonLabel }}
      </button>
    </div>
  </div>

  <!-- Refresh link confirmation modal -->
  <confirmation-modal
    :open="refreshLinkModalOpen"
    :title="t('label.refreshLink')"
    :message="t('text.refreshLinkNotice')"
    :confirm-label="t('label.save')"
    :cancel-label="t('label.cancel')"
    @confirm="() => refreshLinkConfirm()"
    @close="closeRefreshLinkModal"
  ></confirmation-modal>
</template>

<style scoped>
header {
  margin-block-end: 2rem;
}

h2 {
  font-size: 1.5rem;
}

h3 {
  font-size: 0.8125rem;
  font-weight: bold;
  margin-block-end: 0.5rem;
}

.customize-link-input {
  position: relative;
  margin-block-end: 1rem;

  button {
    position: absolute;
    z-index: 99;
    right: 0.875rem;
    bottom: 0.875rem;
    color: var(--colour-apmt-primary);
  }
}

.share-link-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.25rem;
  border: 1px solid var(--colour-neutral-border);
  border-radius: 4px;
  font-size: 0.75rem;

  button {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.5rem;
    background-color: var(--colour-apmt-primary);
    color: var(--colour-neutral-base);
    font-size: 0.75rem;
    border-radius: 4px;

    &:hover {
      background-color: var(--colour-apmt-primary-hover);
    }

    &:active {
      background-color: var(--colour-apmt-primary-pressed);
    }
  }
}
</style>