<script setup lang="ts">
import { inject, ref, useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';
import { callKey } from '@/keys';
import { createUserStore } from '@/stores/user-store';
import { useRouter } from 'vue-router';
import { TextInput, IconButton, ModalDialog, DangerButton, LinkButton, CheckboxInput, NoticeBar, NoticeBarTypes } from '@thunderbirdops/services-ui';
import { PhX } from '@phosphor-icons/vue';
import { Alert, BooleanResponse, Exception } from '@/models';
import { posthog, usePosthog } from '@/composables/posthog';
import { MetricEvents } from '@/definitions';

const { t } = useI18n();
const call = inject(callKey);
const userStore = createUserStore(call);
const router = useRouter();

const deleteModal = useTemplateRef('deleteModal');
const consentToDeletion = ref(false);
const confirmPassword = ref('');
const supportUrl = import.meta.env?.VITE_SUPPORT_URL;
const validationError = ref<Alert>(null);

/**
 * Trigger the actual delete account modal.
 */
const show = () => {
  deleteModal.value?.show();
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

defineExpose({ show })
</script>

<template>
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
