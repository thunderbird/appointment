<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { PhCopy, PhArrowClockwise } from '@phosphor-icons/vue';
import { TextInput, LinkButton } from '@thunderbirdops/services-ui';
import { MetricEvents } from '@/definitions';
import { useUserStore } from '@/stores/user-store';
import { useAvailabilityStore } from '@/stores/availability-store';
import { posthog, usePosthog } from '@/composables/posthog';
import RefreshLinkModal from './components/RefreshLinkModal.vue';

const { t } = useI18n();

const userStore = useUserStore();
const availabilityStore = useAvailabilityStore();
const { currentState } = storeToRefs(availabilityStore);

const emit = defineEmits<{ 'link-refreshed': [] }>();

const refreshLinkModalRef = useTemplateRef('refreshLinkModalRef');
const copyButtonLabel = ref(t('label.copy'));
const refreshingLink = ref(false);
const refreshLinkError = ref('');

const linkSlug = computed({
  get: () => currentState.value.slug || userStore.mySlug,
  set: (value) => {
    availabilityStore.$patch({ currentState: { slug: value } });
  },
});

const shortUrlWithoutProtocol = computed(() => userStore.data.userLink.replace(/https?:\/\//g, ''));

async function refreshLinkConfirm() {
  if (refreshingLink.value) {
    return;
  }

  refreshingLink.value = true;
  refreshLinkError.value = '';

  try {
    const { error } = await userStore.changeSignedUrl();

    if (error) {
      refreshLinkError.value = typeof error === 'string' && error ? error : t('error.refreshLinkError');
      return;
    }

    const { error: profileError } = await userStore.profile();

    if (profileError) {
      // Highly unlikely to happen, but just in case we fail to reload the profile
      refreshLinkError.value = t('error.refreshLinkReloadError');
      return;
    }

    // Update link slug in the "Customize Your Link" text field
    // We need to update both initialState and currentState for the isDirty comparison
    availabilityStore.$patch({
      initialState: { slug: userStore.mySlug },
      currentState: { slug: userStore.mySlug },
    });

    refreshLinkModalRef.value.hide();
    emit('link-refreshed');

    if (usePosthog) {
      posthog.capture(MetricEvents.RefreshLink);
    }
  } catch {
    refreshLinkError.value = t('error.refreshLinkError');
  } finally {
    refreshingLink.value = false;
  }
}

function openRefreshLinkModal() {
  refreshLinkError.value = '';
  refreshLinkModalRef.value.show();
}

async function copyLink() {
  await navigator.clipboard.writeText(userStore.myLink);

  copyButtonLabel.value = t('label.copied');

  setTimeout(() => {
    copyButtonLabel.value = t('label.copy');
  }, 2000);
}
</script>

<script lang="ts">
export default {
  name: 'BookingPageLink',
};
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
      <ph-arrow-clockwise size="24" :aria-label="t('label.refreshLink')" />
    </button>
  </text-input>

  <!-- Share your link -->
  <text-input name="bookingPageLinkInput" class="share-link-input" :model-value="userStore.myLink" readonly>
    {{ t('label.shareYourLink') }}:
    <link-button @click="copyLink">
      <template #iconLeft>
        <ph-copy size="16" />
      </template>

      {{ copyButtonLabel }}
    </link-button>
  </text-input>

  <!-- Refresh link confirmation modal -->
  <refresh-link-modal
    ref="refreshLinkModalRef"
    :loading="refreshingLink"
    :error-message="refreshLinkError"
    @confirmed="refreshLinkConfirm()"
    @dismiss-error="refreshLinkError = ''"
  />
</template>

<style scoped>
header {
  font-family: metropolis;
  font-size: 1.5rem;
  margin-block-end: 1rem;
  color: var(--colour-ti-highlight);
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
  margin-block-end: 2rem;

  button {
    position: absolute;
    z-index: 9;
    right: 0.875rem;
    bottom: 0.6875rem;
    color: var(--colour-ti-secondary);
  }
}

.share-link-input {
  position: relative;
  margin-block-end: 1rem;
  width: 100%;

  button {
    position: absolute;
    display: flex;
    gap: 0.5rem;
    padding: 0.25rem 0.5rem;
    right: 0.25rem;
    bottom: 0;
    color: var(--colour-ti-secondary);
    font-size: 0.75rem;
    z-index: 9;
  }
}

.share-link-input :deep(.tbpro-input-wrapper) {
  width: 84%;
}
</style>
