<script setup lang="ts">
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { IconCopy, IconRefresh } from '@tabler/icons-vue';
import { TextInput } from '@thunderbirdops/services-ui';
import { MetricEvents } from '@/definitions';
import { useUserStore } from '@/stores/user-store';
import { useAvailabilityStore } from '@/stores/availability-store';
import ConfirmationModal from '@/components/ConfirmationModal.vue';
import { posthog, usePosthog } from '@/composables/posthog';

const { t } = useI18n();

const userStore = useUserStore();
const availabilityStore = useAvailabilityStore();
const { currentState } = storeToRefs(availabilityStore);

const refreshLinkModalOpen = ref(false);
const copyButtonLabel = ref(t('label.copy'));

const linkSlug = computed({
  get: () => currentState.value.slug || userStore.mySlug,
  set: (value) => {
    availabilityStore.$patch({ currentState: { slug: value } })
  }
})

const shortUrlWithoutProtocol = computed(() => userStore.data.userLink.replace(/https?:\/\//g, ''))

function openRefreshLinkModal() {
  refreshLinkModalOpen.value = true;
}

function closeRefreshLinkModal() {
  refreshLinkModalOpen.value = false;
}

async function refreshLinkConfirm() {
  await userStore.changeSignedUrl();
  await userStore.profile();

  // Update link slug in the "Customize Your Link" text field
  // We need to update both initialState and currentState for the isDirty comparison
  availabilityStore.$patch({
    initialState: { slug: userStore.mySlug },
    currentState: { slug: userStore.mySlug }
  })

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
    :outer-prefix="shortUrlWithoutProtocol"
    v-model="linkSlug"
  >
    {{ t('label.customizeYourLink') }}:
    <button @click="openRefreshLinkModal">
      <icon-refresh size="20" :aria-label="t('label.refreshLink')" />
    </button>
  </text-input>

  <!-- Share your link -->
  <text-input
    name="shareLink"
    class="share-link-input"
    :model-value="userStore.myLink"
  >
    {{ t('label.shareYourLink') }}:
    <button @click="copyLink">
      <icon-copy size="12" />
      {{ copyButtonLabel }}
    </button>
  </text-input>

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
  font-weight: 600;
  margin-block-end: 0.5rem;
  padding: 0.1875rem;
}

.customize-link-input {
  position: relative;
  margin-block-end: 1rem;

  button {
    position: absolute;
    z-index: 9;
    right: 0.875rem;
    bottom: 0.875rem;
    color: var(--colour-apmt-primary);
  }
}

.share-link-input {
  position: relative;
  margin-block-end: 1rem;

  button {
    position: absolute;
    display: flex;
    gap: 0.25rem;
    padding: 0.25rem 0.5rem;
    right: 0.75rem;
    bottom: 0.75rem;
    align-items: center;
    background-color: var(--colour-apmt-primary);
    color: var(--colour-neutral-base);
    font-size: 0.75rem;
    border-radius: 4px;
    z-index: 9;
  }
}
</style>