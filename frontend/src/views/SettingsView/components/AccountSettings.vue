<script setup lang="ts">
import { computed, inject, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { callKey } from '@/keys';
import { TextInput, IconButton } from '@thunderbirdops/services-ui';
import { PhCopySimple, PhArrowRight, PhDownloadSimple } from '@phosphor-icons/vue';
import { createUserStore } from '@/stores/user-store';
import { useSettingsStore } from '@/stores/settings-store';
import { BlobResponse, BooleanResponse } from '@/models';
import { posthog, usePosthog } from '@/composables/posthog';
import { MetricEvents } from '@/definitions';
import ConfirmationModal from '@/components/ConfirmationModal.vue';

const { t } = useI18n();
const router = useRouter();

const call = inject(callKey);
const userStore = createUserStore(call);
const settingsStore = useSettingsStore();
const { currentState } = storeToRefs(settingsStore);

const copyLinkTooltip = ref(t('label.copyLink'));
const deleteAppointmentDataModalOpen = ref(false);

const displayName = computed({
  get: () => currentState.value.displayName,
  set: (value) => {
    settingsStore.$patch({ currentState: { displayName: value } })
  }
})

// Link copy
const copyLink = async () => {
  await navigator.clipboard.writeText(userStore.myLink);

  copyLinkTooltip.value = t('info.copiedToClipboard');

  setTimeout(() => {
    copyLinkTooltip.value = t('label.copyLink');
  }, 2000);
};

/**
 * Request an appointment data deletion, and then log out.
 */
const actuallyDeleteAccount = async () => {
  deleteAppointmentDataModalOpen.value = false;

  const { error }: BooleanResponse = await call('account/delete').delete();

  if (usePosthog) {
    posthog.capture(MetricEvents.DeleteAccount);
  }

  if (error.value) {
    // TODO: show error
    // console.warn('ERROR: ', error.value);
    return;
  }

  // We can't logout since we've deleted the user by now, so just delete local storage data.
  userStore.$reset();
  await router.push('/');
};

/**
 * Request a data download, and prompt the user to download the data.
 */
const actuallyDownloadData = async () => {
  const { data }: BlobResponse = await call('account/download').post().blob();

  if (!data || !data.value) {
    // TODO: show error
    // console.error('Failed to download blob!!');
    return;
  }

  // Data is a ref to our new blob
  const fileObj = window.URL.createObjectURL(data.value);
  window.location.assign(fileObj);

  if (usePosthog) {
    posthog.capture(MetricEvents.DownloadData);
  }
};
</script>

<template>
  <header>
    <h2>{{ t('heading.accountSettings') }}</h2>
  </header>

  <text-input name="booking-page-display-name" v-model="displayName" class="booking-page-display-name-input">
    {{ t('label.displayName') }}
  </text-input>

  <div class="booking-page-url-input-container">
    <text-input name="booking-page-url" v-model="userStore.myLink" readonly class="booking-page-url-input">
      {{ t('label.bookingPageURL') }}
    </text-input>

    <icon-button aria-labelledby="copy-booking-page-url-button" @click="copyLink" :tooltip="copyLinkTooltip"
      class="copy-url-button" size="medium">
      <ph-copy-simple id="copy-booking-page-url-button" :aria-label="t('label.copy')" />
    </icon-button>

    <router-link to="availability" class="manage-booking-page-link">
      <span>{{ t('label.manageBookingLink') }}</span>
      <ph-arrow-right size="16" />
    </router-link>
  </div>

  <div class="account-settings-buttons-container">
    <button :title="t('label.download')" variant="outline" @click="actuallyDownloadData"
      data-testid="settings-account-download-data-btn" class="download-appointment-data-button">
      <ph-download-simple size="16" />
      {{ t('label.downloadMyData') }}
    </button>

    <hr class="account-settings-divider" />

    <div class="delete-appointment-data-container">
      <button @click="deleteAppointmentDataModalOpen = true">
        {{ t('label.deleteAllAppointmentData') }}
      </button>

      <p>{{ t('label.deleteAllAppointmentDataInfo') }}</p>
    </div>
  </div>

  <!-- Delete Appointment Data modal -->
  <confirmation-modal :open="deleteAppointmentDataModalOpen" :title="t('heading.deleteAppointmentData')"
    :message="t('text.deleteAppointmentDataWarning')" :confirm-label="t('heading.deleteAppointmentData')"
    :cancel-label="t('label.cancel')" :use-caution-button="true" @confirm="actuallyDeleteAccount"
    @close="deleteAppointmentDataModalOpen = false">
  </confirmation-modal>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

header {
  margin-block-end: 1.5rem;
}

h2 {
  color: var(--colour-ti-highlight);
  font-size: 1.5rem;
  font-family: metropolis;
}

.booking-page-display-name-input {
  margin-block-end: 1.5rem;
}

.booking-page-url-input-container {
  position: relative;
  margin-block-end: 2rem;

  .booking-page-url-input {
    margin-block-end: 0.5rem;
  }

  .copy-url-button {
    position: absolute;
    right: 0.5rem;
    top: 2.25rem;
    background-color: var(--colour-neutral-base);
    color: var(--colour-ti-secondary);

    :deep(.tooltip) {
      width: max-content;
    }
  }

  .manage-booking-page-link {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--colour-ti-highlight);
    font-size: 0.75rem;
    text-decoration: underline;
  }
}

.account-settings-buttons-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  align-items: flex-start;

  .download-appointment-data-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    margin: 0;
    padding: 0;
    color: var(--colour-ti-highlight);
    background-color: transparent;
    font-size: 0.75rem;
    text-decoration: underline;
    text-underline-offset: 0.125rem;
  }

  .delete-appointment-data-container {
    display: flex;
    flex-direction: column;
    align-items: flex-start;

    button {
      margin-block-end: 0.5rem;
      background-color: transparent;
      color: var(--colour-ti-critical);
      text-decoration: underline;
      text-underline-offset: 0.125rem;
      font-size: 0.75rem;
      margin: 0;
      padding: 0;
      cursor: pointer;
    }

    p {
      font-size: 0.75rem;
      color: var(--colour-ti-secondary);
    }
  }
}

@media (--md) {
  .booking-page-display-name-container {
    grid-template-columns: 20% 1fr;
  }

  .booking-page-url-container {
    grid-template-columns: 20% 1fr;
  }

  .account-settings-buttons-container {
    grid-template-columns: 1fr 1px 1fr;

    .account-settings-divider {
      border: 0;
      border-inline-start: 1px solid var(--colour-neutral-border);
      min-height: 53px;
    }
  }
}
</style>
