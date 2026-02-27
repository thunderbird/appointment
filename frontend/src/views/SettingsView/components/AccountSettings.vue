<script setup lang="ts">
import { computed, inject, ref, useTemplateRef } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { callKey } from '@/keys';
import { TextInput, IconButton, ModalDialog, DangerButton, LinkButton, CheckboxInput, NoticeBar, NoticeBarTypes } from '@thunderbirdops/services-ui';
import { PhCopySimple, PhArrowRight, PhDownloadSimple, PhX } from '@phosphor-icons/vue';
import { createUserStore } from '@/stores/user-store';
import { useSettingsStore } from '@/stores/settings-store';
import { Alert, BlobResponse, BooleanResponse, Exception } from '@/models';
import { posthog, usePosthog } from '@/composables/posthog';
import { MetricEvents } from '@/definitions';

const { t } = useI18n();
const router = useRouter();

const call = inject(callKey);
const userStore = createUserStore(call);
const settingsStore = useSettingsStore();
const { currentState } = storeToRefs(settingsStore);

const copyLinkTooltip = ref(t('label.copyLink'));

const deleteModal = useTemplateRef('deleteModal');
const consentToDeletion = ref(false);
const confirmPassword = ref('');
const supportUrl = import.meta.env?.VITE_SUPPORT_URL;
const validationError = ref<Alert>(null);

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
 * Reset the form data.
 */
const resetData = () => {
  consentToDeletion.value = false;
  confirmPassword.value = '';
  validationError.value = null;
};

/**
 * Request an appointment data deletion, and then log out.
 */
const actuallyDeleteAccount = async () => {
  const pw = confirmPassword.value;

  const { data, error }: BooleanResponse = await call('account/delete').delete({
    password: pw,
  }).json();

  if (usePosthog) {
    posthog.capture(MetricEvents.DeleteAccount);
  }

  if (error.value) {
    validationError.value = { title: (data.value as Exception).detail as string };
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
      {{ t('label.bookingPageLinkLabel') }}
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
      <button @click="deleteModal?.show()" data-testid="settings-account-delete-data-btn">
        {{ t('label.deleteAllAppointmentData') }}
      </button>

      <p>{{ t('label.deleteAllAppointmentDataInfo') }}</p>
    </div>
  </div>

  <!-- Delete Appointment Data modal -->
  <modal-dialog ref="deleteModal" class="delete-modal" @closed="resetData">
    <template #header>
      {{ t('heading.deleteAppointmentData') }}
    </template>

    <div class="delete-modal-container">
      <notice-bar v-if="validationError" class="notice-bar" :type="NoticeBarTypes.Critical">
        {{ validationError.title }}
        <template #cta>
          <icon-button @click="validationError = null" :title="t('label.close')">
            <ph-x />
          </icon-button>
        </template>
      </notice-bar>
      
      <p><strong>{{ t('text.settings.account.delete.permanenceHint') }}</strong></p>
      <p>{{ t('text.settings.account.delete.impactHint') }}</p>
      <p>{{ t('text.settings.account.delete.tbproHint') }}</p>
      <p>
        <checkbox-input
          name="deletion-consent"
          v-model="consentToDeletion"
          :label="t('text.settings.account.delete.consent')"
          required
          data-testid="account-data-deletion-consent-checkbox"
        />
      </p>
  
      <div class="password-confirmation">
        <text-input
          name="confirm-password"
          v-model="confirmPassword"
          :label="t('text.settings.account.delete.confirm')"
          type="password"
          required
          data-testid="account-data-deletion-confirm-password-input"
        />
        <danger-button
          name="delete"
          :disabled="!consentToDeletion || !confirmPassword"
          @click="actuallyDeleteAccount"
          data-testid="account-data-deletion-confirm-btn"
        >
          {{ t('heading.deleteAppointmentData') }}
        </danger-button>
      </div>
    </div>

    <template #actions>
      <link-button
        name="cancel"
        @click="deleteModal?.hide()"
        class="cancel-button"
        data-testid="account-data-deletion-cancel-btn"
      >
        {{ t('label.cancel') }}
      </link-button>
    </template>

    <template #footer>
      <a :href="supportUrl">
        {{ t('label.support') }}
      </a>
      <span>•</span>
      <router-link to="/privacy">
        {{ t('label.privacyPolicy') }}
      </router-link>
    </template>
  </modal-dialog>
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

.delete-modal {
  .delete-modal-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding-bottom: .25rem;
    
    :deep(.checkbox-control) {
      flex-shrink: 0;
    }

    .password-confirmation {
      display: flex;
      flex-direction: column;
      gap: 1rem;

      label {
        flex-grow: 0.5;
      }
  
      button {
        align-self: flex-start;
        /* margin-top: 1.75rem; */
        line-height: 1.25;
      }
    }
  
  }
  .modal-actions .base.cancel-button {
    color: var(--colour-ti-highlight);
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

  .delete-modal {
    .delete-modal-container {
      .password-confirmation {
        flex-direction: row;
    
        button {
          margin-top: 1.75rem;
        }
      }
    }
  }
}
</style>
